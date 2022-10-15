from enum import unique
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import numpy as np
from tqdm.auto import tqdm




def predict(path, lang = 'hin'):
    file = convert_from_path(path,fmt='jpeg')
    data = {}
    for img in tqdm(file[2:-1]):
        img = np.asarray(img)


        i = 0
        coords = []

        for i in range(img.shape[0]):
            how_long = 0
            for j in range(68, img.shape[1]):
                # print(i,j,img[i][j])
                a = img[i][j].tolist()
                # print(a)
                if a[0] == a[1] == a[2] and a[0] < 100:
                    how_long+=1
                    # print(i, j, how_long)
                else:
                    break

                if how_long >= 10:
                    coords.append(i)
                    break
        
        print(coords, len(coords))

        for i in range(len(coords)-3):
            if i+1 >= len(coords):
                break
            if coords[i] - coords[i+1] >-4:
                j = 1
                while True:
                    if i+j+1 >= len(coords):
                        break

                    if coords[i] - coords[i+1+j] > -4:
                        del coords[i+j]
                        j+=1
                    else:
                        break
        
        print(coords, len(coords))

        j = 0
        for i in range(0, len(coords)-3, 2):
            if i+j+2 == len(coords):
                break
            if coords[i+j+1] - coords[i+j+2] < -50:
                coords.insert(i+1+j ,coords[i+1+j])
                j+=1

        print(coords, len(coords))


                
        width = 505
        start_left = 68
        height = 199

        r_top_inc = 5
        r_left_inc = 358
        r_width = 127
        r_height = 33

        c = 3

        img_matrix = []
        r_matrix = []
        id_matrix = []
        info_matrix = []


        for i in range(0,len(coords),2):
            # print(i,i+1)
            img_matrix.append([])
            r_matrix.append([])
            info_matrix.append([])
            id_matrix.append([])


            for j in range(c):
                img_matrix[-1].append(img[coords[i]:coords[i+1], start_left+j*width:start_left+(j+1)*width])
                r_matrix[-1].append(img_matrix[-1][-1][r_top_inc:r_top_inc+r_height, 250:r_left_inc+r_width])
                info_matrix[-1].append(img_matrix[-1][-1][r_height:, :r_left_inc+10])
                id_matrix[-1].append(img_matrix[-1][-1][r_top_inc:r_top_inc+r_height-4:, 1:105])

        img_ = Image.fromarray(r_matrix[-1][-1])

        text = pytesseract.image_to_string(img_, lang='eng')
        runiqueid = text.rstrip().lstrip()

        print(runiqueid)
        if runiqueid == '':
            continue

        text = pytesseract.image_to_string(Image.fromarray(info_matrix[-1][-1]), lang=lang)

        raw_data_split = text.split('\n')

        delt = 0
        for i in range(len(raw_data_split)):
            residue = raw_data_split[i-delt].replace('-','').replace(":",'').replace(' ','').replace('\u200c','').replace('\n','')
            if lang == 'tam':
                residue = residue.replace('த','').replace('ந்','').replace('ைத ','').replace('பெயர்','')

            if  residue == '':    
                del raw_data_split[i-delt]
                delt+=1

        # print(raw_data_split)
        name = raw_data_split[0].replace(' ૬ ',':').split(':')[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n','')

        # father_name = raw_data_split[1].split(':')[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n','')

        gender = 'M' if 'ஆ' in raw_data_split[-1].split(':')[-1].replace('-','').replace(' ','').replace('\u200c','').replace('\n','') else 'F'

        text = pytesseract.image_to_string(Image.fromarray(info_matrix[-1][-1]))

        raw_data_split = text.split('\n')


        delt = 0
        for i in range(len(raw_data_split)):
            if raw_data_split[i-delt].replace('-','').replace(' ','').replace('\u200c','').replace('\n','') == '':
                del raw_data_split[i-delt]
                delt+=1

        print(raw_data_split)

        try:
            age = int(''.join(raw_data_split[-1].split(':')[:-1]).split(' ')[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''))

        except:
            age = 0

        try:
            house_no = raw_data_split[-2].split(':')[-1].split(' ')[-1].replace(' ','').replace('\u200c','').replace('\n','')

        except:
            house_no = '0'
        
        print(house_no)
        this_data = {'age':age, 'house_no':house_no, 'gender':gender, 'name':name}

        data[runiqueid] = this_data

    return data


import pprint

pprint.pprint(predict('test.pdf', lang='tam'))