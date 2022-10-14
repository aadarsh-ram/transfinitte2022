import imp
import time
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys


all_states = [ "Andhra Pradesh",
                "Arunachal Pradesh",
                "Assam",
                "Bihar",
                "Chhattisgarh",
                "Goa",
                "Gujarat",
                "Haryana",
                "Himachal Pradesh",
                "Jammu and Kashmir",
                "Jharkhand",
                "Karnataka",
                "Kerala",
                "Madhya Pradesh",
                "Maharashtra",
                "Manipur",
                "Meghalaya",
                "Mizoram",
                "Nagaland",
                "Odisha",
                "Punjab",
                "Rajasthan",
                "Sikkim",
                "Tamil Nadu",
                "Telangana",
                "Tripura",
                "Uttarakhand",
                "Uttar Pradesh",
                "West Bengal",
                "Andaman and Nicobar Islands",
                "Chandigarh",
                "Dadra and Nagar Haveli",
                "Daman and Diu",
                "Delhi",
                "Lakshadweep",
                "Puducherry"]

all_states.sort();

for i in range(len(all_states)) :
    all_states[i]=all_states[i].lower();

print(all_states)


def getRequestID(link):

    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Disable GUI

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    chrome_options.add_argument(f'user-agent={user_agent}')

    chrome_options.add_argument("--no-sandbox")

    # Comment if driver already added to PATH
    webdriver_service = Service("/home/shubham/Downloads/chromedriver")
    browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    browser.get(link)
    # print(browser.page_source.encode('utf-8'))
    continue_but = browser.find_element(By.XPATH,'//*[@id="continue"]')
    continue_but.click()
    age = 22;
    age_select = Select(browser.find_element(By.XPATH,'//*[@id="ageList"]'));
    age_select.select_by_visible_text(str(age));
    state = "Tamil Nadu";
    state_select = Select(browser.find_element(By.XPATH,'//*[@id="nameStateList"]'));
    state_select.select_by_visible_text(state);
    name = "Aashish A";
    name_box = browser.find_element(By.XPATH,'//*[@id="name1"]');
    name_box.send_keys(name);
    father_name = "Anantha Ramakrishnan R";
    father_name_box = browser.find_element(By.XPATH,'//*[@id="txtFName"]');
    father_name_box.send_keys(father_name);
    gender = 'M'
    gender_select = Select(browser.find_element(By.XPATH,'//*[@id="listGender"]'))
    gender_select.select_by_value(gender)
    captcha = browser.find_element(By.XPATH,'//*[@id="captchaDetailImg"]');
    with open('filename.png','wb') as file:
            file.write(captcha.screenshot_as_png);

    last_selects = browser.find_elements(By.XPATH,'//*[@id="namelocationList"]');
    time.sleep(2)
    district = 'Chennai'
    district_select = Select(last_selects[0]);
    district_select.select_by_visible_text(district);
    time.sleep(2)
    ass_cons= 'Virugampakkam'
    ass_cons_select_select = Select(last_selects[1]);
    ass_cons_select_select.select_by_visible_text(ass_cons);

    time.sleep(15)

    searchbt = browser.find_elements(By.XPATH,'//*[@id="btnDetailsSubmit"]')[1]
    searchbt.click()

    time.sleep(5)

    viewdetails_but = browser.find_element(By.XPATH,'//*[@id="resultsTable"]/tbody/tr/td[1]/form/input[25]')
    viewdetails_but.click()

    time.sleep(20)

    

    time.sleep(50000)

getRequestID("https://electoralsearch.in/")

