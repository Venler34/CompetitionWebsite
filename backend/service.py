import numpy as np
import pandas as pd
from typing import Dict, Tuple

from .errors import *

def verifyAnswersForElapsedSeconds(predictions, supabase, db_user):
    # 8) Update user score if improved
    updated = ElapsedTimeStrategy.editScore(predictions["elapsed_seconds"], db_user["id"], supabase)

    return {
        "message": (
            f"{'Score updated!' if updated else 'Score not improved; '} "
        )
    }

def verifyAnwersForTimeSeries(supabase, db_user):
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
    col_scores, total_score = TimeSeriesOffsetStrateggy.computeError(answers_sub, predictions)

    # 8) Update user score if improved
    updated = TimeSeriesOffsetStrateggy.editScore(total_score, db_user["id"])

    return {
        "message": (
            f"{'Score updated!' if updated else 'Score not improved; '} "
            f"Total Error: {total_score}"
        ),
        "perColumnScores": col_scores
    }