# backend/ai_engine/prompt_builder.py

def build_prompt(user_query, columns):

    schema = ", ".join(columns)

    prompt = f"""
You are a data analytics assistant.

Dataset columns:
{schema}

User request:
{user_query}

Decide:

1 chart type (bar,line,pie)
1 dimension column
1 metric column

Rules:
- dimension must exist in dataset
- metric must exist in dataset
- metric must be numeric

Return ONLY JSON:

{{
 "chart":"bar",
 "dimension":"model",
 "metric":"price"
}}
"""

    return prompt