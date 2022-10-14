import time
import glob
import os
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from solver import solver_agent


path = 'test_img'
cropped_img_path = 'cropped_img'
solver = solver_agent()

def getRequestID(link, name, age, father_name, gender, state, district, ass_cons):

    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Disable GUI

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')

    chrome_options.add_argument("--no-sandbox")

    # Comment if driver already added to PATH
    webdriver_service = Service("/home/frozenwolf/chromedriver")
    browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    browser.get(link)
    # print(browser.page_source.encode('utf-8'))
    continue_but = browser.find_element(By.XPATH,'//*[@id="continue"]')
    continue_but.click()

    age_select = Select(browser.find_element(By.XPATH,'//*[@id="ageList"]'));
    age_select.select_by_visible_text(str(age));

    state_select = Select(browser.find_element(By.XPATH,'//*[@id="nameStateList"]'));
    state_select.select_by_visible_text(state);

    name_box = browser.find_element(By.XPATH,'//*[@id="name1"]');
    name_box.send_keys(name);

    father_name_box = browser.find_element(By.XPATH,'//*[@id="txtFName"]');
    father_name_box.send_keys(father_name);

    gender_select = Select(browser.find_element(By.XPATH,'//*[@id="listGender"]'))
    gender_select.select_by_value(gender)
    
    last_selects = browser.find_elements(By.XPATH,'//*[@id="namelocationList"]');
    time.sleep(2)
    district_select = Select(last_selects[0]);
    district_select.select_by_visible_text(district);
    
    time.sleep(2)
    ass_cons_select_select = Select(last_selects[1]);
    ass_cons_select_select.select_by_visible_text(ass_cons);

    while True:
        files = glob.glob(path+'/*')
        for f in files:
            os.remove(f)
        files = glob.glob(cropped_img_path+'/*')
        for f in files:
            os.remove(f)
        
        captcha = browser.find_element(By.XPATH,'//*[@id="captchaDetailImg"]');
        with open(path+'/filename.png','wb') as file:
            file.write(captcha.screenshot_as_png);
        prediction = solver.solve(path)

        captchaText = browser.find_element(By.XPATH, '//*[@id="txtCaptcha"]')
        captchaText.send_keys(prediction)

        submitbt = browser.find_elements(By.XPATH,'//*[@id="btnDetailsSubmit"]')[1]
        submitbt.click()

        try:
            time.sleep(1)
            viewdetails_but = browser.find_element(By.XPATH,'//*[@id="resultsTable"]/tbody/tr/td[1]/form/input[25]')
            break
        except:
            continue
    
    time.sleep(3)

    viewdetails_but = browser.find_element(By.XPATH,'//*[@id="resultsTable"]/tbody/tr/td[1]/form/input[25]')
    viewdetails_but.click()

    time.sleep(50000)

getRequestID("https://electoralsearch.in/", "Aashish A", 22, "Anantha Ramakrishnan R", 'M', 'Tamil Nadu', 'Chennai', 'Virugampakkam')