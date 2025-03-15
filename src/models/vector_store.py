from dataclasses import dataclass
from typing import Optional
from enum import Enum

from src.models.embedding import EmbeddingConfig


class DocumentType(Enum):
    """
    Enum representing the possible document types in the vector store.

    Using an enum instead of string literals provides better type safety,
    autocompletion support, and prevents typos in document type references.
    """

    TABLE = "table"
    COLUMN = "column"
    QUERY = "query"

    def __str__(self):
        """
        Returns the string value of the enum member.

        This allows the enum to be used in string contexts like database queries.
        """
        return self.value

    @classmethod
    def from_string(cls, type_str: str) -> "DocumentType":
        """
        Converts a string to the corresponding DocumentType enum value.

        Args:
            type_str: String representation of the document type

        Returns:
            The corresponding DocumentType enum value

        Raises:
            ValueError: If the string doesn't match any valid document type
        """
        for doc_type in cls:
            if doc_type.value == type_str:
                return doc_type
        raise ValueError(f"Invalid document type: {type_str}")


@dataclass
class VectorStoreConfig:
    """
    Configuration for the vector store.

    Contains all the necessary parameters to initialize and connect
    to a vector database for storing and retrieving semantic vectors.

    Attributes:
        type: Type of vector store (e.g., "qdrant")
        collection_name: Name of the collection in the vector store
        path: Path for local storage (optional)
        url: URL for remote server (optional)
        embedding: Configuration for the embedding model
        api_key: API key for remote server authentication (optional)
        batch_size: Number of documents to process in each batch operation
        sync_on_startup: Whether to sync metadata to vector store on startup (default: True)
    """

    type: str
    collection_name: str
    path: Optional[str]
    url: Optional[str]
    embedding: EmbeddingConfig
    api_key: Optional[str] = None
    batch_size: int = 100
    sync_on_startup: bool = True


@dataclass
class TableSearchResult:
    """
    Result of a table search operation in the vector store.

    Contains the matched table metadata along with relevance information.

    Attributes:
        id: Unique identifier of the document in the vector store
        table_name: Name of the matched table
        metadata: Complete metadata of the matched table
        relevance_score: Similarity score between query and table (0-1)
    """

    id: str
    similarity_score: float
    name: str
    columns: list
    primary_keys: list
    foreign_keys: list
    row_count: int
    description: str
    keywords: list
    importance_score: float


@dataclass
class ColumnSearchResult:
    """
    Result of a column search operation in the vector store.

    Contains the matched column metadata along with relevance information.

    Attributes:
        id: Unique identifier of the document in the vector store
        column_name: Name of the matched column
        ai_name: AI-generated alternative name for the column
        table_name: Name of the table containing the column
        metadata: Complete metadata of the matched column
        relevance_score: Similarity score between query and column (0-1)
    """

    id: str
    similarity_score: float
    name: str
    table: str
    data_type: str
    nullable: bool
    is_primary_key: bool
    is_foreign_key: bool
    relationships: list
    ai_name: str
    description: str
    keywords: list


@dataclass
class QuerySearchResult:
    """
    Result of a query search operation in the vector store.

    Contains the matched query information along with relevance score.

    Attributes:
        id: Unique identifier of the document in the vector store
        question: Natural language question that was asked
        sql_query: SQL query that answers the question
        explanation: Explanation of how the SQL query works
        score: Similarity score between input and stored question (0-1)
        positive_votes: Number of positive user feedback received
        metadata: Complete metadata of the matched query (optional)
    """

    id: str
    similarity_score: float
    question: str
    sql_query: str
    explanation: str
    positive_votes: int
