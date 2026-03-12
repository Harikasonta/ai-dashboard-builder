# backend/ai_engine/query_suggestions.py

import pandas as pd


def generate_query_suggestions(df, prompt=None):

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

    suggestions = []

    # Basic aggregations
    for cat in categorical_cols[:3]:
        for num in numeric_cols[:2]:

            suggestions.append(f"{num} by {cat}")
            suggestions.append(f"average {num} by {cat}")

    # Top queries
    if numeric_cols and categorical_cols:

        suggestions.append(f"top 5 {categorical_cols[0]} by {numeric_cols[0]}")

    # Trend queries
    for col in df.columns:
        if "date" in col.lower() or "year" in col.lower():

            if numeric_cols:
                suggestions.append(f"{numeric_cols[0]} trend by {col}")

    return list(set(suggestions))[:8]