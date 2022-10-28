from curses.ascii import isdigit
from enum import unique
from tabnanny import check
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from ai4bharat.transliteration import XlitEngine
import numpy as np
from tqdm.auto import tqdm

def show(img):
    img = Image.fromarray(img)
    img.show()

def predict(path, lang = 'tam'):
    n = 0
    e = XlitEngine(src_script_type="indic", beam_width=10, rescore=False)


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
                else:
                    break

                if how_long >= 10:
                    coords.append(i)
                    break
                
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
        
        j = 0
        for i in range(0, len(coords)-3, 2):
            if i+j+2 == len(coords):
                break
            if coords[i+j+1] - coords[i+j+2] < -50:
                coords.insert(i+1+j ,coords[i+1+j])
                j+=1

                
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

                
                if runiqueid == '':
                    continue

                text = pytesseract.image_to_string(Image.fromarray(info_matrix[-1][-1]), lang=lang)

                raw_data_split = text.split('\n')

                delt = 0

                for i_ in range(len(raw_data_split)):
                    residue = raw_data_split[i_-delt].replace('-','').replace(":",'').replace(' ','').replace('\u200c','').replace('\n','')
                    if residue == '':    
                        del raw_data_split[i_-delt]
                        delt+=1

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

                    if len(raw_data_split)>4 and ("Father" not in raw_data_split[1] and "Husband" not in raw_data_split[1]):
                        raw_data_split[0] = raw_data_split[0] +' ' + raw_data_split[1]
                        raw_data_split.pop(1)

                    elif len(raw_data_split)>4 and ("Father" in raw_data_split[1] and "Husband" in raw_data_split[1]) and "House" not in raw_data_split[2]:
                        raw_data_split[1] = raw_data_split[1] +' ' + raw_data_split[2]
                        raw_data_split.pop(2)   

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
                        gender = 'M'


                    text = pytesseract.image_to_string(Image.fromarray(info_matrix[-1][-1]))
        
                    raw_data_split = text.split('\n')


                    delt = 0
                    for i_ in range(len(raw_data_split)):
                        if raw_data_split[i_-delt].replace('-','').replace(' ','').replace('\u200c','').replace('\n','') == '':
                            del raw_data_split[i_-delt]
                            delt+=1

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

                    house_no = 'd'
                    if ':' not in raw_data_split[-2] and '.' in raw_data_split[-2]:
                        raw_data_split[-2] = raw_data_split[-2].replace('.',':')

                    if len(raw_data_split)>=5:
                        raw_data_split[-3] = raw_data_split[-3] + ' '+ raw_data_split[-2]
                        del raw_data_split[-2]

                    if len(raw_data_split[-2].split(':'))>=2:
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

                if lang == 'tam':
                    husband_father = 'F'
                    if True in ['கணவர்' in i.replace('-','').replace(' ','').replace('\u200c','').replace('\n','') for i in raw_data_split]:
                        husband_father = 'H'

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

                    if (raw_data_split[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n','').replace(":","") == "தந்\u200cைத பெயர்\u200c".replace(' ','').replace('\u200c','')) or raw_data_split[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n','').replace(":","") == "கணவர்\u200c பெயர்\u200c".replace(' ','').replace('\u200c',''):
                        sep = ":" if ":" not in raw_data_split[1] else ""
                        raw_data_split[1]=raw_data_split[1]+sep+" "+raw_data_split[2]
                        del raw_data_split[2]
                        raw_data_split_ = raw_data_split


                    father_name = raw_data_split[1].split(':')[1].replace('-','').replace(' ','').replace('\u200c','').replace('\n','')

                    if 'ஆண்' in raw_data_split[-1].split(':')[-1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''):
                        gender = 'M'

                    elif "பெண்" in raw_data_split[-1].split(':')[-1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''):
                        gender = 'F'

                    elif "பாலினம்" in raw_data_split[-1].split(':')[-1].replace('-','').replace(' ','').replace('\u200c','').replace('\n',''):
                        gender = 'O'
                    else :
                        gender = 'M'

                    text = pytesseract.image_to_string(Image.fromarray(info_matrix[-1][-1]))

                    raw_data_split = text.split('\n')


                    delt = 0
                    for i_ in range(len(raw_data_split)):
                        if raw_data_split[i_-delt].replace('-','').replace(' ','').replace('\u200c','').replace('\n','') == '':
                            del raw_data_split[i_-delt]
                            delt+=1

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

                    if ':' not in raw_data_split[-2] and '.' in raw_data_split[-2]:
                        raw_data_split[-2] = raw_data_split[-2].replace('.',':')

                    if len(raw_data_split)>=5:
                        raw_data_split[-3] = raw_data_split[-3] + ' '+ raw_data_split[-2]
                        del raw_data_split[-2]

                    if len(raw_data_split[-2].split(':'))>=2:
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
                        
                    if name.rstrip().lstrip() != "":
                        try:
                            name = e.translit_word(name, lang_code="ta").replace('\u200c','').replace('\n','')
                        except:
                            pass

                    if father_name.rstrip().lstrip() != "":
                        try:
                            father_name = e.translit_word(father_name, lang_code="ta").replace('\u200c','').replace('\n','')
                        except:
                            pass


                    this_data = {'age':age, 'house_no':house_no, 'gender':gender, 'name':name, 'father/husband':(father_name, husband_father), 'uniqueid':runiqueid}

                    data[runiqueid] = this_data

    return data
