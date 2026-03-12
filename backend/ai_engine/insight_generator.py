# backend/ai_engine/insight_generator.py

def generate_insight(data, metric=None, dimension=None):

    if not data or len(data) < 2:
        return "Not enough data to generate insights."

    # MULTI METRIC CASE
    if metric is None:

        metrics = list(data[0].keys())
        metrics.remove("name")

        insights = []

        for m in metrics:

            highest = max(data, key=lambda x: x[m])
            lowest = min(data, key=lambda x: x[m])

            insights.append(
                f"{highest['name']} has the highest {m} while {lowest['name']} has the lowest."
            )

        return " ".join(insights)

    # SINGLE METRIC CASE
    highest = max(data, key=lambda x: x["value"])
    lowest = min(data, key=lambda x: x["value"])

    return (
        f"{highest['name']} has the highest {metric} "
        f"while {lowest['name']} has the lowest."
    )