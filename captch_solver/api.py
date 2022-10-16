import os
from requests import request
import uvicorn
import pickle
import pprint
from fastapi import FastAPI, Response, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from algo import ALGO
import warnings
from main import SEL_AGENT

from tamilnadu import get_tamilnadupdf
from uttarpradesh import get_uttar_pradesh
from nctdelhi import get_nctdelhipdf
from westbengal import get_westbengalpdf

from OCR import predict

warnings.filterwarnings("ignore")
path_loc = os.path.join(os.getcwd(),'test_pdf')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# @app.on_event("startup")
# async def startup():
#     startupDB()

# @app.on_event("shutdown")
# async def shutdown():
#     shutdownDB()

@app.get('/')
async def home(request: Request):
    return 'hi!'

@app.post('/getpdfinfo')
async def getpdfinfo(request: Request):
    """
    Get pdf from Name, Age, Father Name, Gender, State, District
    """

    browser_agent = SEL_AGENT()
    browser_agent.startupDB()

    incoming_data = await request.json()
    name = incoming_data["name"]
    age = incoming_data["age"]
    fathername = incoming_data["fathername"]
    gender = incoming_data["gender"]
    state = incoming_data["state"]
    district = incoming_data["district"]
    
    part_no,serial_no,epic_id,asc_no,asc,district,state,browser = browser_agent.getRequestID("https://electoralsearch.in/", name, age, fathername, gender, state, district)
    if (state == "Tamil Nadu"):
        
        filename = (get_tamilnadupdf(district, asc, int(part_no), browser))
        x = predict(filename, lang='tam')
        pickle.dump(x, open('output_tam.pkl','wb'))
    
    elif (state == "NCT of Delhi"):

        filename = (get_nctdelhipdf(asc, int(part_no), browser))
        x = predict(filename, lang='eng')
        pickle.dump(x, open('output_tam.pkl','wb'))

    curr = ALGO('output_tam.pkl', epic_id)
    curr.genTree()
    familyTree = curr.created
    print (familyTree)

    return familyTree

if __name__ == '__main__':
    uvicorn.run(app)