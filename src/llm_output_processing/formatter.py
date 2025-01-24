import pandas as pd
from typing import Dict, Any


class QueryResultFormatter:
    @staticmethod
    def format(
        parsed_response: Dict[str, Any], query_result: tuple[bool, Any]
    ) -> Dict[str, Any]:
        """Format the query result in a dictionary to be returned to the user"""
        if not parsed_response["success"]:
            return {
                "success": False,
                "error": parsed_response.get("error", "Error during parsing"),
            }

        query_success, data = query_result
        if not query_success:
            return {
                "success": False,
                "error": data,
                "query": parsed_response["query"],
                "explanation": parsed_response["explanation"],
            }

        columns, rows = data
        df = pd.DataFrame(rows, columns=columns)

        if df.empty:
            return {
                "success": True,
                "query": parsed_response["query"],
                "explanation": parsed_response["explanation"],
                "results": [],
                "preview": [],
            }

        return {
            "success": True,
            "query": parsed_response["query"],
            "explanation": parsed_response["explanation"],
            "results": df.to_dict("records"),
            "preview": df.head().to_dict("records"),
        }
