import time
import glob
import os

from solver import solver_agent
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.support.ui import Select
import selenium.webdriver.support.ui as UI
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


class SEL_AGENT:
    def __init__(self):
        self.path = 'test_img'
        self.cropped_img_path = 'cropped_img'
        self.solver = solver_agent()
        self.path_loc = os.path.join(os.getcwd(),'test_pdf')

        self.chrome_options = Options()
        self.browser = None

        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
        self.chrome_options.add_argument(f'user-agent={self.user_agent}')

        self.chrome_options.add_argument("--no-sandbox")

        self.chrome_options.add_experimental_option('prefs', {
            "download.default_directory": self.path_loc,
            "profile.default_content_settings.popups":0,
            "download.prompt_for_download": False, #To auto download the file
            "download.open_pdf_in_system_reader":False,
            "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
            })

    def startupDB(self):
        # Comment if driver already added to PATH
        self.webdriver_service = Service("/home/frozenwolf/chromedriver")
        self.browser = webdriver.Chrome(service=self.webdriver_service, options=self.chrome_options)

    def shutdownDB(self):
        self.browser.close()

    def getRequestID(self, link, name, age, father_name, gender, state, district):

        self.browser.get(link)
        # print(browser.page_source.encode('utf-8'))
        continue_but = self.browser.find_element(By.XPATH,'//*[@id="continue"]')
        continue_but.click()

        age_select = Select(self.browser.find_element(By.XPATH,'//*[@id="ageList"]'));
        age_select.select_by_visible_text(str(age));

        state_select = Select(self.browser.find_element(By.XPATH,'//*[@id="nameStateList"]'));
        state_select.select_by_visible_text(state);

        name_box = self.browser.find_element(By.XPATH,'//*[@id="name1"]');
        name_box.send_keys(name);

        father_name_box = self.browser.find_element(By.XPATH,'//*[@id="txtFName"]');
        father_name_box.send_keys(father_name);

        gender_select = UI.Select(self.browser.find_element(By.XPATH,'//*[@id="listGender"]'))
        for i in gender_select.options:
            if (i.text == 'Select Gender from List'): continue
            print (i.text)
            if i.text.split('/')[1].lower() == gender.lower():
                i.click()

        last_selects = self.browser.find_elements(By.XPATH,'//*[@id="namelocationList"]');
        time.sleep(2)
        district_select = Select(last_selects[0]);
        district_select.select_by_visible_text(district);

        while True:
            files = glob.glob(self.path+'/*')
            for f in files:
                os.remove(f)
            files = glob.glob(self.cropped_img_path+'/*')
            for f in files:
                os.remove(f)

            captcha = self.browser.find_element(By.XPATH,'//*[@id="captchaDetailImg"]');
            with open(self.path+'/filename.png','wb') as file:
                file.write(captcha.screenshot_as_png);
            prediction = self.solver.solve(self.path)

            captchaText = self.browser.find_element(By.XPATH, '//*[@id="txtCaptcha"]')

            if(prediction==None):
                prediction="dg"

            captchaText.send_keys(prediction)

            submitbt = self.browser.find_elements(By.XPATH,'//*[@id="btnDetailsSubmit"]')[1]
            self.browser.execute_script("arguments[0].click();", submitbt)
            # submitbt.click()

            try:
                time.sleep(1)
                viewdetails_but = self.browser.find_element(By.XPATH,'//*[@id="resultsTable"]/tbody/tr/td[1]/form/input[25]')
                break
            except:
                continue
            
        time.sleep(3)

        viewdetails_but = self.browser.find_element(By.XPATH,'//*[@id="resultsTable"]/tbody/tr/td[1]/form/input[25]')
        self.browser.execute_script("arguments[0].click();", viewdetails_but)

        # viewdetails_but.click()

        time.sleep(15)

        tbs = self.browser.window_handles

        self.browser.switch_to.window(tbs[-1])

        html_src = self.browser.page_source

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
        return(part_no,serial_no,epic_id,asc_no,asc,district,state, self.browser)

    def getRequestEPIC(self, link, epic, state, district):

        self.browser.get(link)
        # print(browser.page_source.encode('utf-8'))
        continue_but = self.browser.find_element(By.XPATH,'//*[@id="continue"]')
        continue_but.click()

        get_epic_btn = self.browser.find_element(By.XPATH, '//*[@id="mainContent"]/div[2]/div/div/ul/li[2]')
        get_epic_btn.click()

        text_epic = self.browser.find_element(By.XPATH, '//*[@id="name"]')
        text_epic.send_keys(epic)

        state_select = Select(self.browser.find_element(By.XPATH,'//*[@id="epicStateList"]'))
        state_select.select_by_visible_text(state)


        while True:
            files = glob.glob(self.path+'/*')
            for f in files:
                os.remove(f)
            files = glob.glob(self.cropped_img_path+'/*')
            for f in files:
                os.remove(f)

            captcha = self.browser.find_element(By.XPATH,'//*[@id="captchaEpicImg"]');
            with open(self.path+'/filename.png','wb') as file:
                file.write(captcha.screenshot_as_png);
            prediction = self.solver.solve(self.path)

            captchaText = self.browser.find_element(By.XPATH, '//*[@id="txtEpicCaptcha"]')

            if(prediction==None):
                prediction="dg"

            captchaText.send_keys(prediction)

            submitbt = self.browser.find_element(By.XPATH,'//*[@id="btnEpicSubmit"]')
            submitbt.click()

            try:
                time.sleep(1)
                viewdetails_but = self.browser.find_element(By.XPATH,'//*[@id="resultsTable"]/tbody/tr/td[1]/form/input[25]')
                break
            except:
                continue
            
            time.sleep(3)

        viewdetails_but = self.browser.find_element(By.XPATH,'//*[@id="resultsTable"]/tbody/tr/td[1]/form/input[25]')
        viewdetails_but.click()

        time.sleep(15)

        tbs = self.browser.window_handles

        self.browser.switch_to.window(tbs[-1])

        html_src = self.browser.page_source

        soup = BeautifulSoup(html_src, 'html.parser')

        asc_inp_tag = soup.find("input", { "id" : "ac_name" })
        asc = asc_inp_tag['value']

        part_no_tag = soup.find("input",{"id":"part_no"})
        part_no = part_no_tag['value']

        serial_no_tag = soup.find("input",{"id":"slno_inpart"})
        serial_no = serial_no_tag['value']

        epic_inp_tag = soup.find("input",{"id":"epic_no"})
        epic_tag = epic_inp_tag.find_next_sibling()
        epic_id = epic_tag.text

        asc_tag2 = asc_inp_tag.find_next_sibling()

        asc_no = ""

        for i in range(len(asc_tag2.text)-1,0,-1):
            if(asc_tag2.text[i]=='-' or asc_tag2.text[i]==' '):
                break
            else:
                asc_no+=asc_tag2.text[i]

        asc_no = asc_no[::-1]
        print (asc_no, part_no, serial_no)
        return(part_no,serial_no,epic_id,asc_no,asc,state,district, self.browser)

    # # part_no,serial_no,epic_id,asc_no,asc,district,state = getRequestID("https://electoralsearch.in/", "Kavita Agraval", 49, "Ekamal Kishor", 'F', 'Uttar Pradesh', 'Ghaziabad', 'Modi Nagar')
    # part_no,serial_no,epic_id,asc_no,asc,state,district = getRequestEPIC("https://electoralsearch.in/", "RAZ2234219", "Tamil Nadu", "Chennai")

    # if(state=="Tamil Nadu"):
    #     print(get_tamilnadupdf(district, asc, int(part_no), browser))

    # elif(state=="Uttar Pradesh"):
    #     print(get_uttar_pradesh(district, asc, part_no, browser))

    # elif(state=="NCT OF Delhi"):
    #     print(get_nctdelhipdf(asc, part_no, browser))

    # # Not working cause captcha tough
    # # get_westbengalpdf("Coochbehar", "Cooch Behar Dakshin", 1, browser) 

    # # Working
# # print(get_nctdelhipdf("Sadar Bazar", 1, browser))

# browser.quit()
