import time
import glob
import os
# from ai4bharat.transliteration import XlitEngine
from selenium.common.exceptions import TimeoutException
import selenium.webdriver.support.ui as UI
from selenium.webdriver.common.by import By
from solver import solver_agent
# from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


path = 'test_img'
cropped_img_path = 'cropped_img'
solver = solver_agent()
path_loc = os.path.join(os.getcwd(),'test_pdf')

files = glob.glob(path_loc+'/*')
latest_file = max(files,key=os.path.getctime)

# e = XlitEngine(src_script_type="indic", beam_width=10, rescore=False)

def get_options_asc(link,asc,browser):
    
    browser.get(link)
    table_element = browser.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/div/div/div/div[2]')
    a_elements = table_element.find_elements(By.XPATH, './div/a')
    for ele in a_elements:
        if (ele.text.split('-')[1].strip().lower() == asc.lower()):
            ele.click()
            time.sleep(1)
            break

def bypass_captcha(browser):
    time.sleep(2)

    while True:
        files = glob.glob(path+'/*')
        for f in files:
            os.remove(f)
        files = glob.glob(cropped_img_path+'/*')
        for f in files:
            os.remove(f)
        
        captcha = browser.find_element(By.XPATH,'//*[@id="ContentPlaceHolder1_imgCaptcha"]')
        with open(path+'/filename.png','wb') as file:
            file.write(captcha.screenshot_as_png);
        
        try:
            prediction = solver.solve(path)
        except:
            prediction = "dummmmy"

        if (prediction == None):
            prediction = "dummmmy"

        captchaText = browser.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_txtCaptcha"]')
        captchaText.clear()
        captchaText.send_keys(prediction)

        submitbt = browser.find_element(By.XPATH,'//*[@id="ContentPlaceHolder1_btnCaptcha"]')
        submitbt.click()

        time.sleep(2)
        check = browser.find_element(By.XPATH, '//*[@id="ContentPlaceHolder1_lblMessage"]')
        if (check.text == "Captcha code is wrong!!"):
            files = glob.glob(path_loc+'/*')
            new_file = max(files,key=os.path.getctime)
            if (new_file == latest_file):
                continue
            else:
                break
        else:
            break

def get_nctdelhipdf(asc,part,browser):
    get_options_asc('https://ceodelhi.gov.in/AcListEng.aspx',asc,browser)

    table = browser.find_element(By.XPATH, '//*[@id="main-content"]/div[2]/div/div/div')
    part_nos = table.find_elements(By.XPATH, './div/div/a')
    for part_no in part_nos:
        if (int(part_no.text) == part):
            part_no.click()
            break

    time.sleep(3)
    child = browser.window_handles[1]
    browser.switch_to.window(child)
    bypass_captcha(browser)

    time.sleep(20)
    
    files = glob.glob(path_loc+'/*')
    latest_file = max(files,key=os.path.getctime)
    return latest_file
