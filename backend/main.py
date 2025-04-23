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
    allow_origins=origins,
    allow_credentials=True,
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
import numpy as np
import pandas as pd
from typing import Dict, Tuple

def computeError(
    answers: pd.DataFrame,
    predictions: pd.DataFrame
) -> Tuple[Dict[str, float], float]:
    """
    For each column in `predictions`:
      rmse     = sqrt(mean((answers[col] - predictions[col])**2))
      cv_rmse  = rmse / mean(answers[col])
      score    = 100 * (1/2) ** cv_rmse

    Returns:
      column_scores: { col_name: score }
      total_score:     sum of column_scores (max = n_cols * 100)
    """
    column_scores: Dict[str, float] = {}
    for col in predictions.columns:
        # 1) RMSE
        mse  = ((answers[col] - predictions[col]) ** 2).mean()
        rmse = np.sqrt(mse)

        # 2) normalize by mean
        meanv = answers[col].mean()
        if meanv != 0:
            x = rmse / meanv
        else:
            # if true values are flat zero, perfect => x=0, else infinite
            x = 0.0 if rmse == 0 else np.inf

        # 3) exponential decay score
        score_col = 100.0 * (1/3) ** (1.5 * x)

        column_scores[col] = round(score_col, 4)

    total_score = round(sum(column_scores.values()), 4)
    return column_scores, total_score


def editScore(score, user_id):
    update_score = {"score": score}
    response = (
        supabase
        .table("Users")
        .update(update_score)
        .eq("id", user_id)
        .lt("score", score)   # only update if new score is higher
        .execute()
    )
    return len(response.data) > 0  # True if DB was updated


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

    # 3) Load answer key
    resp    = supabase.table("StockChallenge").select("*").execute()
    answers = pd.DataFrame(resp.data)

    # 4) Drop date column from both (if present)
    predictions = predictions.drop(columns=["date"], errors="ignore")
    answers     = answers.drop(columns=["date"],     errors="ignore")

    # 5) Enforce 30 rows
    if len(predictions) != len(answers):
        return {"error": f"Your file must have exactly {len(answers)} rows"}

    # 6) Filter to valid tickers only
    valid_tickers      = set(answers.columns)
    user_tickers       = set(predictions.columns)
    valid_user_tickers = list(user_tickers & valid_tickers)

    if not valid_user_tickers:
        return {"error": "No valid tickers found in your upload"}

    predictions = predictions[valid_user_tickers]
    answers_sub = answers[valid_user_tickers]

    # 7) Compute per-column scores and total score
    col_scores, total_score = computeError(answers_sub, predictions)

    # 8) Update user score if improved
    updated = editScore(total_score, db_user["id"])

    return {
        "message": (
            f"{'Score updated!' if updated else 'Score not improved; '} "
            f"Total: {total_score} / {len(answers.columns)*100}"
        ),
        "perColumnScores": col_scores
    }


@app.get("/placements")
def getPlacemenets():
    response = supabase.table("Users").select("*").execute()
    results  = response.data

    # Sort descending: highest score first
    results = sorted(results, key=lambda x: x["score"], reverse=True)

    for r in results:
        # Remove sensitive fields
        r.pop("password",  None)
        r.pop("id",        None)
        r.pop("created_at", None)

    return {"Placements": results}