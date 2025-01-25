from typing import Any
from src.connectors.connector import DatabaseConnector


class SQLQueryExecutor:
    @staticmethod
    def execute(query: str, db: DatabaseConnector) -> tuple[bool, Any]:
        """
        Execute a SQL query and return the result.
        Returns:
            Tuple[bool, Any]: (successo, (columns, data) | None)
        """
        try:
            result = db.execute_query(query)
            return True, result
        except Exception as e:
            return False, f"Error during sql query execution: {str(e)}"
