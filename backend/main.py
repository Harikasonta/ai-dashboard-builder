from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import pandas as pd
import json
import os

from ai_engine.query_suggestions import generate_query_suggestions
from ai_engine.widget_meta import generate_widget_meta
from ai_engine.insight_generator import generate_insight

from groq import Groq
from dotenv import load_dotenv

# ===============================
# LOAD ENV
# ===============================

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ===============================
# FASTAPI SETUP
# ===============================

app = FastAPI(title="AI Dashboard Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# GLOBAL DATA
# ===============================

df = None
DATASET_COLUMNS = []
DATASET_SCHEMA = {}

# ===============================
# REQUEST MODEL
# ===============================

class PromptRequest(BaseModel):
    prompt: str

# ===============================
# HOME
# ===============================

@app.get("/")
def home():
    return {"message": "AI Dashboard API running"}

# ===============================
# SCHEMA DETECTION
# ===============================

def detect_schema(df):

    numeric = df.select_dtypes(include="number").columns.tolist()
    categorical = df.select_dtypes(include="object").columns.tolist()

    date_cols = []

    for col in df.columns:
        if "date" in col.lower() or "year" in col.lower():
            date_cols.append(col)

    return {
        "numeric": numeric,
        "categorical": categorical,
        "date": date_cols
    }

# ===============================
# BUILD SCHEMA CONTEXT
# ===============================

def build_schema_context():

    return f"""
Dataset Columns:
{DATASET_COLUMNS}

Numeric columns:
{DATASET_SCHEMA['numeric']}

Categorical columns:
{DATASET_SCHEMA['categorical']}

Date columns:
{DATASET_SCHEMA['date']}
"""

# ===============================
# AI QUERY PLANNER
# ===============================

def plan_query(prompt):

    schema = build_schema_context()

    instruction = f"""
You are a data analyst AI.

Using the dataset schema below convert the user request into chart instructions.

{schema}

Return ONLY JSON in this format:

{{
 "charts":[
  {{
   "chart":"bar|line|pie|grouped_bar",
   "dimension":"column",
   "metric":"column",
   "metrics":["optional"],
   "aggregation":"avg|sum|count",
   "limit":optional,
   "sort":"asc|desc"
  }}
 ]
}}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": instruction},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    text = response.choices[0].message.content

    text = text.replace("```json", "").replace("```", "").strip()

    start = text.find("{")
    end = text.rfind("}") + 1

    json_str = text[start:end]

    try:
        return json.loads(json_str)

    except:
        return {
            "charts":[
                {
                    "chart":"bar",
                    "dimension": DATASET_SCHEMA["categorical"][0],
                    "metric": DATASET_SCHEMA["numeric"][0]
                }
            ]
        }

# ===============================
# TITLE GENERATOR
# ===============================

def generate_title(chart_type, dimension, metric, metrics=None):

    if metrics:
        return f"Comparison of {' & '.join(metrics)} by {dimension}"

    if chart_type == "pie":
        return f"Distribution of {dimension}"

    if dimension and "year" in dimension.lower():
        return f"{metric.capitalize()} Trend by Year"

    return f"{metric.capitalize()} by {dimension.capitalize()}"

# ===============================
# EXECUTE QUERY PLAN
# ===============================

def execute_plan(plan):

    widgets = []

    for chart in plan["charts"]:

        dimension = chart.get("dimension")
        metric = chart.get("metric")
        metrics = chart.get("metrics")
        aggregation = chart.get("aggregation", "avg")
        limit = chart.get("limit")
        sort = chart.get("sort", "desc")

        if dimension not in df.columns:
            continue

        # ===============================
        # MULTI METRIC
        # ===============================

        if metrics:

            valid_metrics = [m for m in metrics if m in df.columns]

            result = df.groupby(dimension)[valid_metrics].mean().reset_index()

            data = []

            for _, row in result.iterrows():

                entry = {"name": row[dimension]}

                for m in valid_metrics:
                    entry[m] = float(round(row[m], 2))

                data.append(entry)

            meta = generate_widget_meta(data)
            insight = generate_insight(data)

            title = generate_title("grouped_bar", dimension, None, valid_metrics)

            widgets.append({
                "title": title,
                "chart": "grouped_bar",
                "data": data,
                "meta": meta,
                "insight": insight
            })

            continue

        # ===============================
        # SINGLE METRIC
        # ===============================

        if metric not in df.columns:
            continue

        if aggregation == "sum":
            result = df.groupby(dimension)[metric].sum().reset_index()

        elif aggregation == "count":
            result = df.groupby(dimension)[metric].count().reset_index()

        else:
            result = df.groupby(dimension)[metric].mean().reset_index()

        if sort == "desc":
            result = result.sort_values(metric, ascending=False)
        else:
            result = result.sort_values(metric, ascending=True)

        if limit:
            result = result.head(int(limit))

        result.columns = ["name", "value"]

        data = result.to_dict("records")

        meta = generate_widget_meta(data)
        insight = generate_insight(data)

        title = generate_title(chart["chart"], dimension, metric)

        widgets.append({
            "title": title,
            "chart": chart["chart"],
            "data": data,
            "meta": meta,
            "insight": insight
        })

    return widgets

# ===============================
# GENERATE DASHBOARD
# ===============================

@app.post("/generate")
def generate_dashboard(request: PromptRequest):

    global df

    if df is None:
        return {"error": "Upload dataset first"}

    try:

        plan = plan_query(request.prompt)

        widgets = execute_plan(plan)

        suggestions = generate_query_suggestions(df)

        return {
            "widgets": widgets,
            "suggestions": suggestions
        }

    except Exception as e:
        return {"error": str(e)}

# ===============================
# CHAT WITH DASHBOARD
# ===============================

@app.post("/chat")
def chat_dashboard(request: PromptRequest):

    if df is None:
        return {"error": "Upload dataset first"}

    try:

        plan = plan_query(request.prompt)

        widgets = execute_plan(plan)

        return {"widgets": widgets}

    except Exception as e:
        return {"error": str(e)}

# ===============================
# UPLOAD DATASET
# ===============================

@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):

    global df, DATASET_COLUMNS, DATASET_SCHEMA

    df = pd.read_csv(file.file)

    df.columns = df.columns.str.strip()
    df = df.fillna(0)

    DATASET_COLUMNS = list(df.columns)

    DATASET_SCHEMA = detect_schema(df)

    suggestions = generate_query_suggestions(df)

    return {
        "message": "Dataset uploaded",
        "columns": DATASET_COLUMNS,
        "schema": DATASET_SCHEMA,
        "suggestions": suggestions
    }

# ===============================
# CLEAR DATASET
# ===============================

@app.post("/clear-dataset")
def clear_dataset():

    global df, DATASET_COLUMNS, DATASET_SCHEMA

    df = None
    DATASET_COLUMNS = []
    DATASET_SCHEMA = {}

    return {"message": "Dataset cleared"}