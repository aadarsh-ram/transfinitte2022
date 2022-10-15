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



# e = XlitEngine(src_script_type="indic", beam_width=10, rescore=False)

def get_options_dist(link,dist,asc,browser):
    browser.get(link)
    table_elements = browser.find_elements(By.TAG_NAME, "td")
    for ele in table_elements:
        curr_dist = ele.find_element(By.XPATH, "*")
        if (curr_dist.text.lower() == dist.lower()):
            curr_dist.click()
            time.sleep(1)
            get_options_asc(asc, browser)
            break

def get_options_asc(asc,browser):
    table_element = browser.find_element(By.XPATH, '//*[@id="tblACList"]/tbody')
    tr_elements = table_element.find_elements(By.XPATH, './tr/td/a')
    for ele in tr_elements:
        if (ele.text.lower() == asc.lower()):
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
        
        captcha = browser.find_element(By.XPATH,'//*[@id="captcha1"]')
        with open(path+'/filename.png','wb') as file:
            file.write(captcha.screenshot_as_png);
        
        try:
            prediction = solver.solve(path)
        except:
            prediction = "dummmmy"

        if (prediction == None):
            prediction = "dummmmy"

        captchaText = browser.find_element(By.XPATH, '//*[@id="txtSupplement1Capcha"]')
        captchaText.clear()
        captchaText.send_keys(prediction)

        submitbt = browser.find_element(By.XPATH,'//*[@id="btnCapchaSupplement1"]')
        submitbt.click()

        time.sleep(2)
        check = browser.find_element(By.XPATH, '//*[@id="lblMessageSupplement1"]')
        if (check.text == "Invalid Capcha!!!"):
            reload = browser.find_element(By.XPATH, '//*[@id="btnRefreshCapchaSupplement1"]')
            reload.click()
            continue
        else:
            break

def get_westbengalpdf(dist,asc,part,browser):
    get_options_dist('http://ceowestbengal.nic.in/DistrictList#',dist,asc,browser)

    table = browser.find_element(By.XPATH, '//*[@id="tblPSList"]/tbody')
    part_nos = table.find_elements(By.XPATH, './tr/td[1]')
    links = table.find_elements(By.XPATH, './tr/td[4]/a')
    for part_no, link in zip(part_nos, links):
        if (int(part_no.text) == part):
            link.click()
    
    # sub_bt = browser.find_element(By.XPATH,'//*[@id="btn_Login"]')
    # sub_bt.click()
    # par = browser.find_element(By.ID,f"lCustomers_ctrl{part-1}_hl_link1_{part-1}")
    # par.click()
    bypass_captcha(browser)

    # print('hey')

    # src = browser.page_source

    # with open('gg.html','wb') as file:
    #     file.write(browser.page_source.encode('utf-8'))
    #     print('done')

    # soup = BeautifulSoup(src, 'html.parser')

    # iframe = soup.find('iframe')

    # pdf_link = iframe['src']

    # files = glob.glob(path_loc+'/*')
    # for f in files:
    #     os.remove(f)

    # browser.get(pdf_link)

    time.sleep(5)
    
    files = glob.glob(path_loc+'/*')
    latest_file = max(files,key=os.path.getctime)
    return latest_file
