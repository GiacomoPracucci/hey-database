import uuid


class VectorStoreUtils:
    """
    Utility methods for vector store operations.

    Provides static methods for generating deterministic IDs
    and other common vector store operations.
    """

    @staticmethod
    def generate_table_id(table_name: str) -> str:
        """
        Generate a deterministic ID for a table using UUID5.

        UUID5 generates a deterministic UUID based on a namespace and name,
        ensuring the same table always gets the same ID.

        Args:
            table_name: Name of the table

        Returns:
            Deterministic UUID for the table
        """
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"table_{table_name}"))

    @staticmethod
    def generate_column_id(table_name: str, column_name: str) -> str:
        """
        Generate a deterministic ID for a column using UUID5.

        Combines table and column names to ensure uniqueness across
        the entire database schema.

        Args:
            table_name: Name of the table containing the column
            column_name: Name of the column

        Returns:
            Deterministic UUID for the column
        """
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"column_{table_name}_{column_name}"))

    @staticmethod
    def generate_query_id(question: str) -> str:
        """
        Generate a deterministic ID for a query using UUID5.

        Uses the question text to generate a consistent ID, allowing
        for detection of duplicate questions and updates to existing entries.

        Args:
            question: The user's question text

        Returns:
            Deterministic UUID for the query
        """
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, question))
