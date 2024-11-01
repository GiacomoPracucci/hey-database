from pandas import DataFrame
import logging
from src.dbcontext.postgres_metadata_retriever import PostgresMetadataRetriever
from src.prompt.prompt_manager import PromptManager
from dotenv import load_dotenv
import os
load_dotenv()

logger = logging.getLogger(__name__)

class ChatService:
    """Classe che gestisce la logica del servizio di chat"""
    def __init__(self, db, llm_manager):
        self.db = db
        self.db.connect()
        self.llm_manager = llm_manager
        
        self.schema_manager = PostgresMetadataRetriever(self.db.engine, schema="video_games")
        self.prompt_manager = PromptManager(self.schema_manager, self.db)
    
    def process_message(self, message: str) -> dict:
        """ Elabora un messaggio dell'utente, interroga il modello e restituisce i risultati formattati"""
        logger.debug(f"Processing message: {message}")
        try:
            prompt = self.prompt_manager.generate_prompt(message)
            logger.debug(f"Generated prompt: {prompt}")

            llm_response = self.llm_manager.get_completion(prompt)
            logger.debug(f"LLM response: {llm_response}")

            results = self.prompt_manager.process_query(llm_response)
            logger.debug(f"Query results: {results}")

            if results["success"]:
                if isinstance(results.get("results"), DataFrame):
                    results["results"] = results["results"].to_dict('records')
                if isinstance(results.get("preview"), DataFrame):
                    results["preview"] = results["preview"].to_dict('records')
            
            return results
            
        except Exception as e:
            logger.exception(f"Error processing message: {str(e)}")
            return {
                "success": False,
                "error": f"Errore nell'elaborazione del messaggio: {str(e)}"
            }
            
    def __del__(self):
        """Chiude le connessioni quando l'oggetto viene distrutto"""
        if hasattr(self, 'db'):
            self.db.close()