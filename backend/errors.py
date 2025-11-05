import numpy as np
import pandas as pd
from typing import Dict, Tuple

class ElapsedTimeStrategy():
    # Score is represented as elapsed time
    @staticmethod
    def editScore(score, user_id, supabase):
        print("Updating score", score, user_id)
        update_score = {"score": score}
        response = (
            supabase
            .table("Users")
            .update(update_score)
            .eq("id", user_id)
            .gt("elapsed_seconds", score)   # only update if new score is smaller
            .execute()
        )
        return len(response.data) > 0  # True if DB was updated
    

# Score is based is the summation of your model prediction errors from actual value
class ErrorOffsetStrategy():
    @staticmethod
    def computeError(answers: pd.DataFrame, predictions: pd.DataFrame) -> Tuple[Dict[str, float], float]:
        """
        For each column in `predictions`:
        Computes difference in prediction and answers and sums the result
        """
        column_scores: Dict[str, float] = {}
        for col in predictions.columns:
            error = (answers[col] - predictions[col]).abs().sum()
            column_scores[col] = round(error, 4)

        total_score = round(sum(column_scores.values()), 4)
        return column_scores, total_score
    
    @staticmethod
    def editScore(score, user_id, supabase):
        update_score = {"score": score}
        response = (
            supabase
            .table("Users")
            .update(update_score)
            .eq("id", user_id)
            .gt("score", score)   # only update if new score is smaller
            .execute()
        )
        return len(response.data) > 0  # True if DB was updated


class TimeSeriesOffsetStrateggy():
    @staticmethod
    def computeError(answers: pd.DataFrame, predictions: pd.DataFrame) -> Tuple[Dict[str, float], float]:
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
            score_col = 100.0 * (1/10) ** (100.0 * x)
            column_scores[col] = round(score_col, 4)

        total_score = round(sum(column_scores.values()), 4)
        return column_scores, total_score
    
    @staticmethod
    def editScore(score, user_id, supabase):
        update_score = {"score": score}
        response = (
            supabase
            .table("Users")
            .update(update_score)
            .eq("id", user_id)
            .gt("score", score)   # only update if less error than before
            .execute()
        )
        return len(response.data) > 0  # True if DB was updated