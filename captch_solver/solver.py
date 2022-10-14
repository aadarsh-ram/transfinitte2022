import sys
import os
import time
import argparse

import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
from torch.autograd import Variable

from PIL import Image
import string
import argparse

import torch
import torch.backends.cudnn as cudnn
import torch.utils.data
import torch.nn.functional as F

from utils import CTCLabelConverter, AttnLabelConverter
from dataset import RawDataset, AlignCollate
from model import Model
import cv2
from skimage import io
import numpy as np
import craft_utils
import test
import test_CRAFT
import imgproc
import file_utils
import json
import string
import pandas as pd
from crop_img import *
from craft import CRAFT

from collections import OrderedDict

class ARGS:
    trained_model='craft_mlt_25k.pth'
    text_threshold=0.7
    low_text=0.4
    link_threshold=0.4
    cuda=True
    canvas_size=1280
    mag_ratio=1.5
    poly=False
    show_time=False
    test_folder='/data/'
    refine=False
    refiner_model='craft_refiner_CTW1500.pth'


class OPTION:
    image_folder = None
    saved_model = 'TPS-ResNet-BiLSTM-Attn-case-sensitive.pth'
    workers=4
    batch_size=192
    batch_max_length=25
    imgH=32
    imgW=100
    rgb= False
    character = '0123456789abcdefghijklmnopqrstuvwxyz'
    sensitive = True
    PAD = False

    Transformation = 'TPS'
    FeatureExtraction = 'ResNet'
    SequenceModeling='BiLSTM'
    Prediction='Attn'
    num_fiducial = 20
    input_channel= 1
    output_channel = 512
    hidden_size = 256

args = ARGS()
opt = OPTION()

def str2bool(v):
    return v.lower() in ("yes", "y", "true", "t", "1")

def demo(opt, model, converter):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


    # prepare data. two demo images from https://github.com/bgshih/crnn#run-demo
    AlignCollate_demo = AlignCollate(imgH=opt.imgH, imgW=opt.imgW, keep_ratio_with_pad=opt.PAD)
    demo_data = RawDataset(root=opt.image_folder, opt=opt)  # use RawDataset
    demo_loader = torch.utils.data.DataLoader(
        demo_data, batch_size=opt.batch_size,
        shuffle=False,
        num_workers=int(opt.workers),
        collate_fn=AlignCollate_demo, pin_memory=True)

    # predict
    model.eval()
    with torch.no_grad():
        for image_tensors, image_path_list in demo_loader:
            batch_size = image_tensors.size(0)
            image = image_tensors.to(device)
            # For max length prediction
            length_for_pred = torch.IntTensor([opt.batch_max_length] * batch_size).to(device)
            text_for_pred = torch.LongTensor(batch_size, opt.batch_max_length + 1).fill_(0).to(device)

            if 'CTC' in opt.Prediction:
                preds = model(image, text_for_pred)

                # Select max probabilty (greedy decoding) then decode index to character
                preds_size = torch.IntTensor([preds.size(1)] * batch_size)
                _, preds_index = preds.max(2)
                # preds_index = preds_index.view(-1)
                preds_str = converter.decode(preds_index, preds_size)

            else:
                preds = model(image, text_for_pred, is_train=False)

                # select max probabilty (greedy decoding) then decode index to character
                _, preds_index = preds.max(2)
                preds_str = converter.decode(preds_index, length_for_pred)


            log = open(f'./log_demo_result.txt', 'a')
            dashed_line = '-' * 80
            head = f'{"image_path":25s}\t{"predicted_labels":25s}\tconfidence score'
            
            print(f'{dashed_line}\n{head}\n{dashed_line}')
            log.write(f'{dashed_line}\n{head}\n{dashed_line}\n')

            preds_prob = F.softmax(preds, dim=2)
            preds_max_prob, _ = preds_prob.max(dim=2)
            for img_name, pred, pred_max_prob in zip(image_path_list, preds_str, preds_max_prob):
                if 'Attn' in opt.Prediction:
                    pred_EOS = pred.find('[s]')
                    pred = pred[:pred_EOS]  # prune after "end of sentence" token ([s])
                    pred_max_prob = pred_max_prob[:pred_EOS]

                # calculate confidence score (= multiply of pred_max_prob)
                confidence_score = pred_max_prob.cumprod(dim=0)[-1]

                print(f'{img_name:25s}\t{pred:25s}\t{confidence_score:0.4f}')
                return pred
                log.write(f'{img_name:25s}\t{pred:25s}\t{confidence_score:0.4f}\n')

            log.close()

class solver_agent:
    def __init__(self):
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.cuda = torch.cuda.is_available()
        # load net
        self.net = CRAFT()     # initialize

        # print('Loading weights from checkpoint (' + args.trained_model + ')')
        if self.cuda:
            self.net.load_state_dict(test_CRAFT.copyStateDict(torch.load(args.trained_model)))
        else:
            self.net.load_state_dict(test_CRAFT.copyStateDict(torch.load(args.trained_model, map_location='cpu')))

        if self.cuda:
            self.net = self.net.cuda()
            self.net = torch.nn.DataParallel(self.net)
            cudnn.benchmark = False

        if opt.sensitive:
              opt.character = string.printable[:-6]  

        if 'CTC' in opt.Prediction:
            self.converter = CTCLabelConverter(opt.character)
        else:
            self.converter = AttnLabelConverter(opt.character)
        opt.num_class = len(self.converter.character)

        if opt.rgb:
            opt.input_channel = 3
        
        self.model = Model(opt)
        print('model input parameters', opt.imgH, opt.imgW, opt.num_fiducial, opt.input_channel, opt.output_channel,
              opt.hidden_size, opt.num_class, opt.batch_max_length, opt.Transformation, opt.FeatureExtraction,
              opt.SequenceModeling, opt.Prediction)
        self.model = torch.nn.DataParallel(self.model).to(device)

        # load model
        print('loading pretrained model from %s' % opt.saved_model)
        self.model.load_state_dict(torch.load(opt.saved_model, map_location=device))

        self.net.eval()

    def solve(self, path):
        start = path

        image_list, _, _ = file_utils.get_files(path)

        image_names = []
        image_paths = []

        for num in range(len(image_list)):
          image_names.append(os.path.relpath(image_list[num], start))

        result_folder = './Results'
        if not os.path.isdir(result_folder):
            os.mkdir(result_folder)

        for num in range(len(image_list)):
          image_names.append(os.path.relpath(image_list[num], start))

        data=pd.DataFrame(columns=['image_name', 'word_bboxes', 'pred_words', 'align_text'])
        data['image_name'] = image_names

        for k, image_path in enumerate(image_list):
            print("Test image {:d}/{:d}: {:s}".format(k+1, len(image_list), image_path), end='\r')
            image = imgproc.loadImage(image_path)

            bboxes, polys, score_text, det_scores = test_CRAFT.test_net(self.net, image, 0.7, 0.4, 0.4, self.cuda, False, args, None)

            bbox_score={}

            for box_num in range(len(bboxes)):
              key = str (det_scores[box_num])
              item = bboxes[box_num]
              bbox_score[key]=item

            data['word_bboxes'][k]=bbox_score
            # save score text
            filename, file_ext = os.path.splitext(os.path.basename(image_path))
            mask_file = result_folder + "/res_" + filename + '_mask.jpg'
            cv2.imwrite(mask_file, score_text)

            file_utils.saveResult(image_path, image[:,:,::-1], polys, dirname=result_folder)

        data.to_csv('data.csv', sep = ',', na_rep='Unknown')

        data=pd.read_csv('data.csv')

        start = path
        for image_num in range(data.shape[0]):
            image = cv2.imread(os.path.join(start, data['image_name'][image_num]))
            image_name = data['image_name'][image_num].strip('.jpeg')
            score_bbox = data['word_bboxes'][image_num].split('),')

            if score_bbox == ['Unknown']:
                continue
            print(image_name)

            generate_words(image_name, score_bbox, image)


        cudnn.benchmark = True
        cudnn.deterministic = True
        opt.num_gpu = torch.cuda.device_count()

        opt.image_folder = 'cropped_img'
        return demo(opt, self.model, self.converter)


# solver = solver_agent()

# solver.solve('test_img')