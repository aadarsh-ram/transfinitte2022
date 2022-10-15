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
from bs4 import BeautifulSoup
from tamilnadu import get_tamilnadupdf


path = 'test_img'
cropped_img_path = 'cropped_img'
solver = solver_agent()
path_loc = os.path.join(os.getcwd(),'test_pdf')


chrome_options = Options()
# chrome_options.add_argument("--headless") # Disable GUI

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')

chrome_options.add_argument("--no-sandbox")

chrome_options.add_experimental_option('prefs', {
"download.default_directory":path_loc,
"profile.default_content_settings.popups":0,
"download.prompt_for_download": False, #To auto download the file
"download.open_pdf_in_system_reader":False,
"plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
})

# Comment if driver already added to PATH
webdriver_service = Service("/home/shubham/Downloads/chromedriver")
browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)

def getRequestID(link, name, age, father_name, gender, state, district, ass_cons):

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

    time.sleep(15)

    tbs = browser.window_handles

    for i in tbs:
        if(i!=browser.current_window_handle):
            browser.switch_to.window(i)
            break

    print('here')

    html_src = browser.page_source

    soup = BeautifulSoup(html_src, 'html.parser')

    asc_inp_tag = soup.find("input", { "id" : "ac_name" })
    asc = asc_inp_tag['value']

    part_no_tag = soup.find("input",{"id":"part_no"})
    part_no = part_no_tag['value']

    serial_no_tag = soup.find("input",{"id":"slno_inpart"})
    serial_no = serial_no_tag['value']

    epic_inp_tag = soup.find("input",{"id":"epic_no"})
    epic_tag = epic_inp_tag.find_next_sibling()
    print(epic_tag.text)
    epic_id = epic_tag.text

    asc_tag2 = asc_inp_tag.find_next_sibling()

    asc_no = ""

    for i in range(len(asc_tag2.text)-1,0,-1):
        if(asc_tag2.text[i]=='-' or asc_tag2.text[i]==' '):
            break
        else:
            asc_no+=asc_tag2.text[i]
    
    asc_no = asc_no[::-1]
    return(part_no,serial_no,epic_id,asc_no,asc,district)

part_no,serial_no,epic_id,asc_no,asc,district = getRequestID("https://electoralsearch.in/", "Aashish A", 22, "Anantha Ramakrishnan R", 'M', 'Tamil Nadu', 'Chennai', 'Virugampakkam')

pdf_path = get_tamilnadupdf(district,asc,int(part_no),browser)

print(pdf_path)

browser.quit()
