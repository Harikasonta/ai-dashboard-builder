# backend/ai_engine/chart_selector.py

import pandas as pd


def select_chart(dimension, metric, df, user_query=None):

    # if query mentions distribution
    if user_query:
        q = user_query.lower()

        if "distribution" in q or "share" in q or "percentage" in q:
            return "pie"

    # time based columns → line chart
    if dimension.lower() in ["year", "date", "month", "day"]:
        return "line"

    # numeric dimension often indicates time / sequence
    if pd.api.types.is_numeric_dtype(df[dimension]):
        return "line"

    # categorical dimension → bar chart
    return "bar"