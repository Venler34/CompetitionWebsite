from fastapi import FastAPI, Depends, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from service import verifyAnswersForElapsedSeconds
from supabase_client import supabase
from pydantic import BaseModel
import pandas as pd
from io import StringIO
import json
import numpy as np

app = FastAPI()

########
# CORS #
########

origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

#######################
# User Authentication #
#######################

# May have potential issue if one user makes multiple accounts, but you can't really stop them in that case

class UserAuth(BaseModel):
    name: str
    password: str

@app.post("/signup")
def create_user(user: UserAuth):
    try:
        response = supabase.table("Users").insert({
            "name": user.name,
            "password": user.password,
            "score": 2147483647
        }).execute()
        return {"message": "User added successfully", "data": response.data}
    except Exception as e:
        return {"message": "Error adding user", "data": str(e)} # Most likely because names are same

def authenticate_user(user: UserAuth):
    response = supabase.table("Users").select("*").eq("name", user.name).eq("password", user.password).execute()

    if(len(response.data) == 0):
        return None, False

    return response.data[0], True

##################
# Score Handling #
##################

@app.post("/verifyAnswers")
async def verifyAnswers(data: str = Form(...), file: UploadFile = File(...)):
    # 1) Authenticate
    user = UserAuth(**json.loads(data))
    db_user, valid_user = authenticate_user(user)
    if not valid_user:
        return {"error": "Invalid user credentials"}

    # 2) Load CSV
    if not file.filename.endswith('.csv'):
        return {"error": "The uploaded file must be a CSV"}
    contents    = await file.read()
    predictions = pd.read_csv(StringIO(contents.decode('utf-8')))

    return verifyAnswersForElapsedSeconds(predictions, supabase, db_user)


@app.get("/placements")
def getPlacemenets():
    response = supabase.table("Users").select("*").execute()
    results  = response.data

    # Sort ascending so lowest elapsed seconds first
    results = sorted(results, key=lambda x: x["score"])

    print("Results", results)

    for r in results:
        # Remove sensitive fields
        r.pop("password",  None)
        r.pop("id",        None)
        r.pop("created_at", None)

    return {"Placements": results}