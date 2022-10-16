import os
import uvicorn
import pickle
import pprint
from fastapi import FastAPI, Response, Request
from fastapi.middleware.cors import CORSMiddleware

from main import getRequestID
from main import startupDB
from main import shutdownDB

from tamilnadu import get_tamilnadupdf
from uttarpradesh import get_uttar_pradesh
from nctdelhi import get_nctdelhipdf
from westbengal import get_westbengalpdf

from OCR import predict


path_loc = os.path.join(os.getcwd(),'test_pdf')

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup():
    startupDB()

@app.on_event("shutdown")
async def shutdown():
    shutdownDB()

@app.post('/getpdfinfo')
async def get_pdf_info(request: Request):
    """
    Get pdf from Name, Age, Father Name, Gender, State, District
    """
    incomingData = await request.json()
    name = incomingData["name"]
    age = incomingData["age"]
    fathername = incomingData["fathername"]
    gender = incomingData["gender"]
    state = incomingData["state"]
    district = incomingData["district"]
    part_no,serial_no,epic_id,asc_no,asc,district,state,browser = getRequestID("https://electoralsearch.in/", name, age, fathername, gender, state, district)
    if (state == "Tamil Nadu"):
        filename = (get_tamilnadupdf(district, asc, int(part_no), browser))
        x = predict(filename, lang='tam')
        pickle.dump(x, open('output_tam.pkl','wb'))
        return "done!"

if __name__ == '__main__':
    uvicorn.run(app, port=5000)