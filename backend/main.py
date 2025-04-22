from fastapi import FastAPI, Depends, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
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
    allow_origins = origins,
    allow_credentials=True,
    allow_methods = ["*"],
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
            "password": user.password
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
def computeError(answers: pd.DataFrame, predictions: pd.DataFrame):
    # RMSE
    resultDF = np.square(answers.subtract(predictions))
    total_sum = resultDF.values.sum()
    total_sum /= resultDF.size
    return np.sqrt(total_sum)

def editScore(score, user_id):
    update_score = {"score": score}
    response = (
        supabase
        .table("Users")
        .update(update_score)
        .eq("id", user_id)
        .gt("score", score)
        .execute()
    )  # EDIT THIS IF SCORE NEEDS TO BE DECREASED
    return len(response.data) > 0 # return true if data was updated otherwise score wasn't high enough

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
    contents = await file.read()
    predictions = pd.read_csv(StringIO(contents.decode('utf-8')))

    # 3) Load answer key
    resp = supabase.table("StockChallenge").select("*").execute()
    answers = pd.DataFrame(resp.data)

    # 4) Drop date column from both
    predictions = predictions.drop(columns=["date"], errors="ignore")
    answers     = answers.drop(columns=["date"],     errors="ignore")

    # 5) Enforce 30 rows
    if len(predictions) != len(answers):
        return {"error": f"Your file must have exactly {len(answers)} rows"}

    # 6) Identify valid tickers and drop the rest
    valid_tickers      = set(answers.columns)
    user_tickers       = set(predictions.columns)
    valid_user_tickers = list(user_tickers & valid_tickers)

    if not valid_user_tickers:
        return {"error": "No valid tickers found in your upload"}

    # keep only valid cols
    predictions = predictions[valid_user_tickers]
    answers_sub = answers[valid_user_tickers]

    # 7) Compute error (RMSE over just the valid tickers)
    error = round(computeError(answers_sub, predictions), 4)

    # 8) Update score if improved
    if not editScore(error, db_user["id"]):
        return {"message": f"Score not improved; your RMSE was {error}"}

    return {"message": f"Score updated! Your RMSE is {error}"}


@app.get("/placements")
def getPlacemenets():
    response = supabase.table("Users").select("*").execute()
    results = response.data

    results = sorted(results, key= lambda x: x['score'], reverse=False) # Lower score comes first because RMSE
    for result in results:
        result.pop('password', None) # Don't leak database info
        result.pop('id', None)
        result.pop('created_at', None)

    return {"Placements" : results}