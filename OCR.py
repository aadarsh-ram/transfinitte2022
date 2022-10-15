from curses.ascii import isdigit
from enum import unique
from tabnanny import check
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import numpy as np
from tqdm.auto import tqdm
import cv2

def show(img):
    # img = cv2.resize(img,(img.shape[0]*2, img.shape[1]*2))
    img = Image.fromarray(img)
    img.show()

def predict(path, lang = 'tam'):
    n = 0
    file = convert_from_path(path,fmt='jpeg')
    data = {}
    for img in tqdm(file[2:-1]): #13
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
        
        # print(coords, len(coords))
        
        if coords[0]-coords[1]>-4 and coords[1]-coords[2]<-100:
            del coords[1]

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
        
        # print(coords, len(coords))

        j = 0
        for i in range(0, len(coords)-3, 2):
            if i+j+2 == len(coords):
                break
            if coords[i+j+1] - coords[i+j+2] < -50:
                coords.insert(i+1+j ,coords[i+1+j])
                j+=1

        # print(coords, len(coords))


                
        width = 505
        start_left = 68
        height = 199

        r_top_inc = 5
        r_left_inc = 358
        r_width = 130
        r_height = 33

        c = 3

        img_matrix = []
        r_matrix = []
        id_matrix = []
        info_matrix = []

        # print(coords)

        for i in range(0,len(coords),2):
            # print(i,i+1)
            img_matrix.append([])
            r_matrix.append([])
            info_matrix.append([])
            id_matrix.append([])


            for j in range(c):
                # print(r_top_inc, r_top_inc+r_height, 250, r_left_inc+r_width)
                # print(coords[i], coords[i+1], start_left+j*width, start_left+(j+1)*width)
                img_matrix[-1].append(img[coords[i]:coords[i+1], start_left+j*width:start_left+(j+1)*width])
                # print(i,j,img_matrix[-1][-1].shape)
                r_matrix[-1].append(img_matrix[-1][-1][r_top_inc:r_top_inc+r_height, 250:r_left_inc+r_width])
                info_matrix[-1].append(img_matrix[-1][-1][r_height:, :r_left_inc+10])
                id_matrix[-1].append(img_matrix[-1][-1][r_top_inc:r_top_inc+r_height-4:, 1:105])


                # print(r_matrix[-1][-1].shape)
                img_ = Image.fromarray(r_matrix[-1][-1])

                text = pytesseract.image_to_string(img_, lang='eng')
                runiqueid = text.rstrip().lstrip()

                
                # print(runiqueid)
                if runiqueid == '':
                    continue

                # show(info_matrix[-1][-1])
                # show(info_matrix[-1][-1])
                text = pytesseract.image_to_string(Image.fromarray(info_matrix[-1][-1]), lang=lang)

                raw_data_split = text.split('\n')

                delt = 0
                # print(raw_data_split)

                # if ':' not in raw_data_split[1] and :

                for i_ in range(len(raw_data_split)):
                    residue = raw_data_split[i_-delt].replace('-','').replace(":",'').replace(' ','').replace('\u200c','').replace('\n','')
                    # if lang == 'tam':
                    #     if residue.replace('த','').replace('ந்','').replace('ைத ','').replace('பெயர்','') == '' and :

                    if  residue == '':    
                        del raw_data_split[i_-delt]
                        delt+=1

                # print(raw_data_split)

                if lang == 'eng':
                    husband_father = 'H'
                    if True in ['Father' in i.replace('-','').replace(' ','').replace('\u200c','').replace('\n','') for i in raw_data_split]:
                        husband_father = 'F'   

                    if "=" in raw_data_split[1] and ":" not in raw_data_split[1]:
                        raw_data_split[1] = raw_data_split[1].replace("=",":")

                    if "|" in raw_data_split[1] and ":" not in raw_data_split[1]:
                        raw_data_split[1] = raw_data_split[1].replace("|",":")

                    if "-" in raw_data_split[1] and ":" not in raw_data_split[1]:
                        raw_data_split[1] = raw_data_split[1].replace("-",":")

                    if "-" in raw_data_split[0] and ":" not in raw_data_split[0]:
                        raw_data_split[0] = raw_data_split[0].replace("-",":")

                    elif ":" not in raw_data_split[0] and "Name" not in raw_data_split[0]:
                        raw_data_split[0] = "Name :"+raw_data_split[0]

                    elif ":" not in raw_data_split[0] and "Name" in raw_data_split[0]:
                        raw_data_split[0] = " :"+raw_data_split[0]

                    # print(raw_data_split)

                    if len(raw_data_split)>4 and ("Father" not in raw_data_split[1] and "Husband" not in raw_data_split[1]):
                        raw_data_split[0] = raw_data_split[0] +' ' + raw_data_split[1]
                        raw_data_split.pop(1)

                    elif len(raw_data_split)>4 and ("Father" in raw_data_split[1] and "Husband" in raw_data_split[1]) and "House" not in raw_data_split[2]:
                        raw_data_split[1] = raw_data_split[1] +' ' + raw_data_split[2]
                        raw_data_split.pop(2)   


                            
                        
                    # show(info_matrix[-1][-1])
                    # print(raw_data_split)
                    raw_data_split_ = raw_data_split
                    name = raw_data_split[0].split(':')[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n','')


                    if True in ['Mother' in i.replace('-','').replace(' ','').replace('\u200c','').replace('\n','') for i in raw_data_split]:
                        continue

                    if True in ['Wife' in i.replace('-','').replace(' ','').replace('\u200c','').replace('\n','') for i in raw_data_split]:
                        continue

                    father_name = None
                    
                    try:
                        father_name = raw_data_split[1].split(':')[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n','')

                    except:
                        pass

                    if 'MALE' in raw_data_split[-1].split(':')[-1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''):
                        gender = 'M'

                    elif "FEMALE" in raw_data_split[-1].split(':')[-1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''):
                        gender = 'F'

                    elif "OTHER" in raw_data_split[-1].split(':')[-1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''):
                        gender = 'O'
                    else :
                           # if runiqueid == "RAZ161654¢":
                           #     continue
                           # show(img_matrix[-1][-1])
                           # 0/0
                        gender = 'M'


                    text = pytesseract.image_to_string(Image.fromarray(info_matrix[-1][-1]))
        
                    raw_data_split = text.split('\n')


                    delt = 0
                    for i_ in range(len(raw_data_split)):
                        if raw_data_split[i_-delt].replace('-','').replace(' ','').replace('\u200c','').replace('\n','') == '':
                            del raw_data_split[i_-delt]
                            delt+=1

                    # print(raw_data_split)
                    age = 28

                    try:
                        age = int(''.join(raw_data_split[-1].split(':')[:-1]).split(' ')[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''))

                    except:
                        try:
                            if len(raw_data_split) == 5 and True in [i.isdigit() for i in raw_data_split]:
                                age = int(''.join(raw_data_split[-2].split(':')[:-1]).split(' ')[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''))

                        except:
                            try:
                                age = int(raw_data_split_[-1].split(':')[-2].split(' ')[1])
                            except:
                                age = 28

                    # print(raw_data_split)

                    house_no = 'd'
                    if ':' not in raw_data_split[-2] and '.' in raw_data_split[-2]:
                        raw_data_split[-2] = raw_data_split[-2].replace('.',':')

                    # print(raw_data_split[-2].split(':')
                    if len(raw_data_split)>=5:
                        raw_data_split[-3] = raw_data_split[-3] + ' '+ raw_data_split[-2]
                        del raw_data_split[-2]

                    if len(raw_data_split[-2].split(':'))>=2:
                        # print(raw_data_split[-2].split(':')[1].split(' '))

                        try:
                            house_no = raw_data_split[-2].split(':')[1].split(' ')[1].replace('\u200c','').replace('\n','')
                        except:
                            pass
                        
                    if True not in [i.isdigit() for i in house_no]:
                        try:
                            house_no = raw_data_split[-2].split(':')[1].split(' ')[-1].replace('\u200c','').replace('\n','')
                        except:
                            pass
                        
                    if True not in [i.isdigit() for i in house_no] and ":" in raw_data_split[-1]:
                        try:
                            if len(raw_data_split[-1].split(':'))>=3:
                                house_no = raw_data_split[-1].split(':')[-2].split(' ')[1].replace('\u200c','').replace('\n','')

                            elif len(raw_data_split[-1].split(':'))==2:
                                house_no = raw_data_split[-1].split(':')[-1].split(' ')[1].replace('\u200c','').replace('\n','')
                        except:
                            pass
                        
                    try:
                        if True not in [i.isdigit() for i in house_no]:
                            for i_ in raw_data_split[-2].split(':')[1].split(' '):
                                if i_.isdigit():
                                    house_no = i_
                    except:
                        pass


                    if True not in [i.isdigit() for i in house_no]:
                        house_no = '-1'

                    this_data = {'age':age, 'house_no':house_no, 'gender':gender, 'name':name, 'father/husband':(father_name, husband_father), 'uniqueid':runiqueid}

                    data[runiqueid] = this_data


                    # print(this_data, end="\n\n")





                if lang == 'tam':
                    husband_father = 'F'
                    if True in ['கணவர்' in i.replace('-','').replace(' ','').replace('\u200c','').replace('\n','') for i in raw_data_split]:
                        husband_father = 'H'



                    # print(raw_data_split)
                    raw_data_split_ = raw_data_split
                    name = raw_data_split[0].replace(' ૬ ',':').split(':')[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n','')

                    if ("தந்" and "cைத" and "பெயர்" not in raw_data_split[1]) and "கணவர்" not in raw_data_split[1]:
                        raw_data_split[0] = raw_data_split[0] + raw_data_split[1]
                        del raw_data_split[1]
                        raw_data_split_ = raw_data_split

                    if len(raw_data_split) >=5:
                        if ":" in raw_data_split[1]:
                            raw_data_split[1] = raw_data_split[1] + " "+ raw_data_split[2]
                            del raw_data_split[2]

                    if ":" not in raw_data_split[1] and "." in raw_data_split[1]:
                        raw_data_split[1] = raw_data_split[1].replace(".",":")
                        raw_data_split_ = raw_data_split

                    # print(raw_data_split[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''))
                    if (raw_data_split[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n','').replace(":","") == "தந்\u200cைத பெயர்\u200c".replace(' ','').replace('\u200c','')) or raw_data_split[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n','').replace(":","") == "கணவர்\u200c பெயர்\u200c".replace(' ','').replace('\u200c',''):
                        sep = ":" if ":" not in raw_data_split[1] else ""
                        raw_data_split[1]=raw_data_split[1]+sep+" "+raw_data_split[2]
                        del raw_data_split[2]
                        raw_data_split_ = raw_data_split


                    # print(raw_data_split)
                    father_name = raw_data_split[1].split(':')[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n','')


                    # print(raw_data_split[-1].split(':')[-1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''))

                    if 'ஆண்' in raw_data_split[-1].split(':')[-1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''):
                        gender = 'M'

                    elif "பெண்" in raw_data_split[-1].split(':')[-1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''):
                        gender = 'F'

                    elif "பாலினம்" in raw_data_split[-1].split(':')[-1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''):
                        gender = 'O'
                    else :
                        # if runiqueid == "RAZ161654¢":
                        #     continue
                        # show(img_matrix[-1][-1])
                        # 0/0
                        gender = 'M'

                    text = pytesseract.image_to_string(Image.fromarray(info_matrix[-1][-1]))

                    raw_data_split = text.split('\n')


                    delt = 0
                    for i_ in range(len(raw_data_split)):
                        if raw_data_split[i_-delt].replace('-','').replace(' ','').replace('\u200c','').replace('\n','') == '':
                            del raw_data_split[i_-delt]
                            delt+=1

                    # print(raw_data_split)

                    try:
                        age = int(''.join(raw_data_split[-1].split(':')[:-1]).split(' ')[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''))

                    except:
                        try:
                            if len(raw_data_split) == 5 and True in [i.isdigit() for i in raw_data_split]:
                                age = int(''.join(raw_data_split[-2].split(':')[:-1]).split(' ')[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''))

                        except:
                            try:
                                age = int(raw_data_split_[-1].split(':')[-2].split(' ')[1])
                            except:
                                age = 28

                    # print(raw_data_split)


                    if ':' not in raw_data_split[-2] and '.' in raw_data_split[-2]:
                        raw_data_split[-2] = raw_data_split[-2].replace('.',':')

                    # print(raw_data_split[-2].split(':')
                    if len(raw_data_split)>=5:
                        raw_data_split[-3] = raw_data_split[-3] + ' '+ raw_data_split[-2]
                        del raw_data_split[-2]

                    if len(raw_data_split[-2].split(':'))>=2:
                        # print(raw_data_split[-2].split(':')[1].split(' '))

                        try:
                            house_no = raw_data_split[-2].split(':')[1].split(' ')[1].replace('\u200c','').replace('\n','')
                        except:
                            pass

                    if True not in [i.isdigit() for i in house_no]:
                        try:
                            house_no = raw_data_split[-2].split(':')[1].split(' ')[-1].replace('\u200c','').replace('\n','')
                        except:
                            pass

                    if True not in [i.isdigit() for i in house_no] and ":" in raw_data_split[-1]:
                        try:
                            if len(raw_data_split[-1].split(':'))>=3:
                                house_no = raw_data_split[-1].split(':')[-2].split(' ')[1].replace('\u200c','').replace('\n','')

                            elif len(raw_data_split[-1].split(':'))==2:
                                house_no = raw_data_split[-1].split(':')[-1].split(' ')[1].replace('\u200c','').replace('\n','')
                        except:
                            pass

                    try:
                        if True not in [i.isdigit() for i in house_no]:
                            for i_ in raw_data_split[-2].split(':')[1].split(' '):
                                if i_.isdigit():
                                    house_no = i_
                    except:
                        pass
                    # if True not in [i.isdigit() for i in raw_data_split[-2].split(':')[1].split(' ')]:

                    # if True not in [i.isdigit() for i in house_no]:
                    #     house_no = raw_data_split[-2].split(':')[1].split(' ')[1]
                    # if house_no !=
                    # except:
                    #     0/0
                    #     house_no = raw_data_split_[-2].split(':')[-1].split(' ')[-1]

                    # no_nums = True
                    # if True not in [i.isdigit() for i in house_no]:
                    #     for i in raw_data_split[::-1]:
                    #         for j in i.split(' '):
                    #             number = ''
                    #             for k in j:
                    #                 if k.isdigit():
                    #                     number+=k

                    #             if number != '':
                    #                 house_no = number
                    #                 no_nums = False
                    #                 break


                    if True not in [i.isdigit() for i in house_no]:
                        house_no = '-1'

                    this_data = {'age':age, 'house_no':house_no, 'gender':gender, 'name':name, 'father/husband':(father_name, husband_father), 'uniqueid':runiqueid}

                    data[runiqueid] = this_data


                    # print(this_data, end="\n\n")

                # show(info_matrix[-1][-1])

                    


    return data

import pprint
a = predict('test_aad.pdf', lang='tam')

import pickle

pickle.dump(a, open('output_tam.pkl','wb'))

pprint.pprint(a)
