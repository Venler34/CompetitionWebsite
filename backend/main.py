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


# Updates score if the score is greater than previous score
def editScore(score, user_id):
    update_score = {"score": score}
    response = supabase.table("Users").update(update_score).eq("id", user_id).lt("score", score).execute()

    return len(response.data) > 0 # return true if data was updated otherwise score wasn't high enough
    
def isValidDataframe(predictions, answers):
    rows, cols = predictions.shape
    answerRows, answerCols = answers.shape
    print(rows, cols)
    print(answerRows, answerCols)
    if(rows != answerRows or cols != answerCols): # 30 rows and 7 columns
        return False, "Number of rows and cols is not correct"

    for (predCol, answerCol) in zip(predictions.columns.tolist(), answers.columns.tolist()):
        if predCol != answerCol:
            return False, f"{predCol} is not a valid column name or the csv is formatted incorrectly"
    
    return True, "No Error"

@app.post("/verifyAnswers")
async def verifyAnswers(data: str = Form(...), file: UploadFile = File(...)):
    print(data)
    user = UserAuth(**json.loads(data))
    print(user.name, user.password)
    db_user, valid_user = authenticate_user(user)
    if(not valid_user):
        return {"error": "Invalid user credentials"}
    
    print("Found User")

    if not file.filename.endswith('.csv'):
        return {"error": "The uploaded file must be a CSV"}
    
    print("CSV Found")

    contents = await file.read()
    predictions = pd.read_csv(StringIO(contents.decode('utf-8')))

    response = supabase.table("StockChallenge").select("*").execute()
    answers = pd.DataFrame(response.data)

    # Check to make sure csv is valid
    isValid, errMsg = isValidDataframe(predictions, answers)
    if(not isValid):
        return {"error", errMsg}

    # Remove date column since unnecessary
    answers.drop("date")
    predictions.drop("date")

    error = computeError(answers, predictions)

    editScore(error, db_user['id']) 

    return {
        "message" : f"Successfully Submitted with RMSE error {error}"
    }

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