from .prompt_builder import build_prompt
from .response_formatter import format_response
from .ai_client import generate_ai_response
from .rule_parser import rule_parse


class QueryParser:

    def parse(self, user_query, columns, df):

        # Step 1: Try rule-based parser first
        rule_result = rule_parse(user_query, columns, df)

        if rule_result:
            print("Rule parser used")
            return rule_result

        # Step 2: Fallback to AI parser
        print("AI parser used")

        prompt = build_prompt(user_query, columns)

        ai_text = generate_ai_response(prompt)

        result = format_response(ai_text)

        return result