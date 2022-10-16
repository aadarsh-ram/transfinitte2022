import os
import uvicorn
import pickle
import pprint
from fastapi import FastAPI, Response, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from algo import ALGO

from main import SEL_AGENT

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
async def getpdfinfo(
    name : str = Form(...),
    age : str = Form(...),
    fathername : str = Form(...),
    gender : str = Form(...),
    state : str = Form(...),
    district : str = Form(...)
):
    """
    Get pdf from Name, Age, Father Name, Gender, State, District
    """

    browser_agent = SEL_AGENT()
    browser_agent.startupDB()
    
    part_no,serial_no,epic_id,asc_no,asc,district,state,browser = browser_agent.getRequestID("https://electoralsearch.in/", name, age, fathername, gender, state, district)
    if (state == "Tamil Nadu"):
        
        filename = (get_tamilnadupdf(district, asc, int(part_no), browser))
        x = predict(filename, lang='tam')
        pickle.dump(x, open('output_tam.pkl','wb'))
        curr = ALGO('output_tam.pkl', epic_id)
        curr.genTree()
        familyTree = curr.created
        print (familyTree)

        return familyTree

if __name__ == '__main__':
    uvicorn.run(app, port=8000, host='0.0.0.0')