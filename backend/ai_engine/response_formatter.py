# backend/ai_engine/response_formatter.py

import json


def format_response(ai_text):

    if ai_text is None:
        raise ValueError("AI returned empty response")

    cleaned = ai_text.replace("```json", "").replace("```", "").strip()

    try:

        return json.loads(cleaned)

    except Exception as e:

        raise ValueError(f"Invalid JSON from AI: {e}")