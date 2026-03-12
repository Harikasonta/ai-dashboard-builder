import re


def rule_parse(query, columns, df):

    q = query.lower()

    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    categorical_cols = df.select_dtypes(include=["object"]).columns

    metrics = []
    dimension = None
    limit = None

    # detect dimension
    for col in categorical_cols:
        if col.lower() in q:
            dimension = col

    # detect numeric metrics
    for col in numeric_cols:
        if col.lower() in q:
            metrics.append(col)

    # detect compare keyword
    if "compare" in q and len(metrics) >= 2 and dimension:

        return {
            "chart": "grouped_bar",
            "dimension": dimension,
            "metrics": metrics[:2],
            "aggregation": "avg"
        }

    # detect top N
    match = re.search(r"top\s*(\d+)", q)
    if match:
        limit = int(match.group(1))

    # fallback single metric
    if metrics and dimension:
        return {
            "chart": "bar",
            "dimension": dimension,
            "metric": metrics[0],
            "aggregation": "avg",
            "limit": limit,
            "sort": "desc"
        }

    return None