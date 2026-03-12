# backend/ai_engine/schema_validator.py

import re
from difflib import get_close_matches


def validate_columns(query, columns):

    query = query.lower()

    # extract potential column names
    words = re.findall(r"[a-zA-Z_]+", query)

    detected_columns = []

    for word in words:
        if word in [c.lower() for c in columns]:
            detected_columns.append(word)
        else:
            # check if it is close to a real column
            match = get_close_matches(word, columns, n=1, cutoff=0.8)
            if match:
                return {
                    "invalid": word,
                    "suggestion": match[0]
                }

    # detect words after "by"
    if "by" in words:
        idx = words.index("by")

        if idx + 1 < len(words):
            col = words[idx + 1]

            if col not in [c.lower() for c in columns]:
                return {
                    "invalid": col,
                    "suggestion": f"Available columns: {', '.join(columns)}"
                }

    return None