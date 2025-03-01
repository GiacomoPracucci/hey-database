from src.rag.strategy import RAGStrategy
from src.rag.models import RAGContext, RAGResponse


class QueryUnderstandingStrategy(RAGStrategy[RAGContext, RAGContext]):
    """
    Strategy interface for understanding and processing the user query.

    Implementations of this strategy might analyze the query,
    extract entities, rewrite the query for better retrieval,
    or classify the query type.
    """

    pass


class RetrievalStrategy(RAGStrategy[RAGContext, RAGContext]):
    """
    Strategy interface for retrieving relevant information from data sources.

    Implementations of this strategy populate the context with
    relevant tables, columns, and previous queries from the vector store
    or other data sources.
    """

    pass


class ContextProcessingStrategy(RAGStrategy[RAGContext, RAGContext]):
    """
    Strategy interface for processing and transforming retrieved context.

    Implementations of this strategy might filter, rank, merge,
    or format the retrieved information to prepare it for prompt creation.
    """

    pass


class PromptBuildingStrategy(RAGStrategy[RAGContext, RAGContext]):
    """
    Strategy interface for constructing prompts for the LLM.

    Implementations of this strategy create a prompt using the
    processed context and original/processed query.
    """

    pass


class LLMInteractionStrategy(RAGStrategy[RAGContext, RAGContext]):
    """
    Strategy interface for interacting with the LLM.

    Implementations of this strategy send the prompt to the LLM
    and receive the response, handling any specific interaction
    patterns like streaming or chain-of-thought prompting.
    """

    pass


class ResponseProcessingStrategy(RAGStrategy[RAGContext, RAGResponse]):
    """
    Strategy interface for processing the LLM response.

    Implementations of this strategy transform the LLM response
    into the final response format, potentially adding citations,
    structuring the output, or performing other post-processing.
    """

    pass
