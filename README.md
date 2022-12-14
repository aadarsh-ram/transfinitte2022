# Transfinitte 2022

Problem Statement: [BharatX] [Build a Family Tree](https://quartz-artichoke-67d.notion.site/Hackathon-Problem-Statement-7f6ebf8bbc694cd18c355eb9433d1197)

Team Name: Project ONN

Contributors:
- [Aadarsh A](https://github.com/aadarsh-ram)
- [Gokul Adethya T](https://github.com/FrozenWolf-Cyber/)
- [Shubham Agarwal](https://github.com/shubham-1806)
- [Pratyush Mantha](https://github.com/pratyush-1)
- [Selvanayagam S](https://github.com/S-Selvanayagam)
- [Kevin Christ](https://github.com/zabarudo)

## Local Setup Instructions

Steps to setup the API:
1. Clone the repo
2. Change working directory 
```
cd captch_solver
```
3. Create a virtualenv
```
python -m venv venv
```
4. Activate the created virtualenv
```
. venv/bin/activate
```
5. Execute the following command:
```
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-tam
```
6. Install all the requirements (Note: There are a lot of dependencies, hence it might take some time)
```
pip install -r requirements.txt
```
7. Download the model files for CRAFT model from [here](https://drive.google.com/file/d/1Jk4eGD7crsqCCg9C9VjCLkMN3ze8kutZ/view) and for TPS-ResNet-BiLSTM-Attn-case-sensitive from [here](https://drive.google.com/file/d/1ajONZOgiG9pEYsQ-eBmgkVbMDuHgPCaY/view) and place them both inside the [captch_solver](https://github.com/aadarsh-ram/transfinitte2022/tree/main/captch_solver) folder.

8. Change the Chrome Driver filepath in this [line](https://github.com/aadarsh-ram/transfinitte2022/blob/main/captch_solver/main.py#L41) to the path where your Chrome Driver has been installed.
(Download the Chrome Driver corresponding to your Google Chrome version [here](https://chromedriver.chromium.org/downloads))

9. Run the API using the following command (Note: Our captcha and transliteration model needs time to setup, it might take some time to get the API started)
```
python3 api.py
```
10. Visit `localhost:8000` to check if the API is working.
11. To search any records, send a POST request to `localhost:8000/getpdfinfo` in the following JSON format.
```
{
    "name" : "<Some name>",
    "age" : "<Some number>",
    "fathername" : "<Some name>",
    "gender" : "<M or F or O>",
    "state" : "<Some state>",
    "district" : "<Some district>"
}
```
These requests take some time to process (~7 min), since we download the file each time and run OCR on it.

12. We also have a UI through which you can enter the above information and a JSON will be returned in the console window of your browser. Visit [this link](./frontend/test.html) to check that out.

A sample response from the API will look like this:
```
{
    "<EPIC NO>": {
        "info": {
            "age": <number>,
            "house_no": "<number>",
            "gender": "<M or F or O>",
            "name": "<name>",
            "father/husband": [
                "<name>",
                "<F or H>"
            ],
            "uniqueid": "<EPIC NO>"
        },
        "children": [<List of names>],
        "spouse": "<Name>",
        "parents": [<List of names>],
        "same": []
    }
}
```
The keys returned in this JSON are self-explanatory.

## States supported
We can take requests for Tamil Nadu and NCT of Delhi currently. Automation scripts for Uttar Pradesh and West Bengal have been written, but have not been implemented in the API.

## Novelty
- We have not used any external API's for finding these family trees, and used only open-source software to build this app. 
- Our captcha solver can work for multilingual text too, which makes it a robust solver for many situations.
- OCR accuracy during conversion of PDFs to text has been improved using special mathematical algorithms created from scratch.

## Tech Stack
- Selenium (for automation)
- AI4Bharat Indic-Transliteration (translating between regional languages)
- Resnet Bi-LSTM Attention (captcha text detection)
- Tessaract OCR (captcha text recognition)

## Main Files
- [API - api.py](./captch_solver/api.py)
- [Captcha Solver - solver.py](./captch_solver/solver.py)
- [OCR Program for PDF Files - OCR.py](./captch_solver/OCR.py)
- [Main Program - main.py](./captch_solver/main.py)
- [Tamil Nadu Automation - tamilnadu.py](./captch_solver/tamilnadu.py)
- [NCT of Delhi Automation - nctdelhi.py](./captch_solver/nctdelhi.py)
- [Algorithm for Family Tree - algo.py](./captch_solver/algo.py)
