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


path = 'test_img'
cropped_img_path = 'cropped_img'
solver = solver_agent()
path_loc = os.path.join(os.getcwd(),'test_pdf')



e = XlitEngine(src_script_type="indic", beam_width=10, rescore=False)

def get_options_dist(link,dist,asc,browser):
    browser.get(link)
    sel_box = browser.find_element(By.XPATH,'//*[@id="ddl_District"]')
    selector = UI.Select(sel_box)
    for i in selector.options :
        out = e.translit_word(i.text, lang_code="ta", topk=5)
        if(dist.lower() in out):
            i.click()
            get_options_asc(asc,browser)
            break


def get_options_asc(asc,browser):
    sel_box = browser.find_element(By.XPATH,'//*[@id="ddl_Assembly"]')
    selector = UI.Select(sel_box)
    for i in selector.options :
        out = e.translit_word(i.text, lang_code="ta", topk=5)
        if(asc.lower() in out):
            i.click()
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
        
        captcha = browser.find_element(By.XPATH,'//*[@id="Image2"]')
        with open(path+'/filename.png','wb') as file:
            file.write(captcha.screenshot_as_png);
        
        try:
            prediction = solver.solve(path)
        except:
            prediction = "dummmmy"

        if (prediction == None):
            prediction = "dummmmy"

        captchaText = browser.find_element(By.XPATH, '//*[@id="txt_Vcode"]')
        captchaText.clear()
        captchaText.send_keys(prediction)

        submitbt = browser.find_element(By.XPATH,'//*[@id="btn_Login"]')
        submitbt.click()

        try:
            WebDriverWait(browser,1).until(EC.alert_is_present())
            alert = browser.switch_to.alert
            alert.accept()
            continue
        except TimeoutException:
            break

def get_tamilnadupdf(dist,asc,part,browser):
    try:
        dist_to_sel = get_options_dist('https://www.elections.tn.gov.in/rollpdf/SSR2022_MR_05012022.aspx',dist,asc,browser)
        sub_bt = browser.find_element(By.XPATH,'//*[@id="btn_Login"]')
        sub_bt.click()
        par = browser.find_element(By.ID,f"lvCustomers_ctrl{part-1}_hl_link1_{part-1}")
        par.click()
        bypass_captcha(browser)

        src = browser.page_source

        with open('gg.html','wb') as file:
            file.write(browser.page_source.encode('utf-8'))
            print('done')

        soup = BeautifulSoup(src, 'html.parser')

        iframe = soup.find('iframe')

        pdf_link = iframe['src']

        files = glob.glob(path_loc+'/*')
        for f in files:
            os.remove(f)

        browser.get(pdf_link)

        time.sleep(5)
        
        files = glob.glob(path_loc+'/*')
        latest_file = max(files,key=os.path.getctime)
        return latest_file
    except:
        browser.close()
        return None