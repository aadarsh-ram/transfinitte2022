from re import sub
import time
import glob
import os
from ai4bharat.transliteration import XlitEngine
from selenium.common.exceptions import TimeoutException
import selenium.webdriver.support.ui as UI
from selenium.webdriver.common.by import By
from solver import solver_agent
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


path = 'test_img'
cropped_img_path = 'cropped_img'
solver = solver_agent()
path_loc = os.path.join(os.getcwd(),'test_pdf')

def get_uttar_pradesh(dist,asc,part,browser):

    browser.get('https://ceouttarpradesh.nic.in//rollpdf/rollpdf.aspx')
    time.sleep(5)

    dist_select =  Select(browser.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_DDLDistrict"]'))
    dist_select.select_by_visible_text(dist)
    ac_select = Select(browser.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_DDL_AC"]'))
    ac_select.select_by_visible_text(asc)
    sbt_btn = browser.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_Button1"]')
    sbt_btn.click()
    clicks = int(part)//20
    modulus = int(part)%20
    if(modulus==0):
        clicks-=1
    if(clicks>0):
        next_btn = browser.find_element(By.XPATH,f'//*[@id="ctl00_ContentPlaceHolder1_ElecRollGrd"]/tbody/tr[22]/td/table/tbody/tr/td[{clicks+1}]/a')
        next_btn.click()
    time.sleep(3)
    vno = int(part)%20
    if(vno==0):
        vno=20
    vstr=""
    if(vno<=8):
        vstr="0"+str(vno+1)
    else:
        vstr=str(vno+1)
    view_btn = browser.find_element(By.XPATH,f'//*[@id="ctl00_ContentPlaceHolder1_ElecRollGrd_ctl{vstr}_p1"]')
    view_btn.click()

    time.sleep(5)

    tbs = browser.window_handles

    browser.switch_to.window(tbs[-1])


    with open('gg.html','wb') as file:
        file.write(browser.page_source.encode('utf-8'))

    files = glob.glob(path_loc+'/*')
    for f in files:
        os.remove(f)


    while True:
        files = glob.glob(path+'/*')
        for f in files:
            os.remove(f)
        files = glob.glob(cropped_img_path+'/*')
        for f in files:
            os.remove(f)
        
        captcha = browser.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_Image1"]')
        with open(path+'/filename.png','wb') as file:
            file.write(captcha.screenshot_as_png);
        
        try:
            prediction = solver.solve(path)
        except:
            prediction = "dummmmy"

        if (prediction == None):
            prediction = "dummmmy"

        captchaText = browser.find_element(By.XPATH, '//*[@id="ctl00_ContentPlaceHolder1_txtimgcode"]')
        captchaText.clear()
        captchaText.send_keys(prediction)

        submitbt = browser.find_element(By.XPATH,'//*[@id="ctl00_ContentPlaceHolder1_Button1"]')
        submitbt.click()

        try:
            WebDriverWait(browser,1).until(EC.alert_is_present())
            alert = browser.switch_to.alert
            alert.accept()
            continue
        except TimeoutException:
            files = glob.glob(path_loc+'/*')
            latest_file = max(files,key=os.path.getctime)
            time.sleep(5)
            return latest_file



