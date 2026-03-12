def generate_widget_meta(data):

    if not data:
        return {}

    # find top performer
    top = max(data, key=lambda x: x.get("value", 0))

    # find lowest
    lowest = min(data, key=lambda x: x.get("value", 0))

    # growth indicator
    growth = None

    if len(data) >= 2:
        start = data[0].get("value",0)
        end = data[-1].get("value",0)

        if start != 0:
            growth = round(((end-start)/start)*100,2)

    return {
        "top_performer": top,
        "lowest": lowest,
        "growth": growth
    }