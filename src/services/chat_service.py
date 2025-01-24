from src.llm_handler.llm_handler import LLMHandler
import logging

logger = logging.getLogger("hey-database")


class ChatService:
    def __init__(self, llm: LLMHandler):
        self.llm = llm

    def process_message(self, message: str) -> dict:
        """Process user message and return formatted results"""
        response = self.sql_agent.run(message)

        return {
            "success": response.success,
            "query": response.query,
            "explanation": response.explanation,
            "results": response.results,
            "preview": response.preview,
            "error": response.error,
            "from_vector_store": response.from_vector_store,
            "original_question": response.original_question,
        }

    def handle_feedback(self, question: str, sql_query: str, explanation: str) -> bool:
        """Delega la gestione del feedback all'SQLAgent"""
        return self.sql_agent.handle_feedback(question, sql_query, explanation)
