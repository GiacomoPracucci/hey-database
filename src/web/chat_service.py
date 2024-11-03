from pandas import DataFrame
import logging
from src.dbcontext.base_metadata_retriever import DatabaseMetadataRetriever
from src.llm_input.prompt_generator import PromptGenerator
from src.llm_output.response_handler import ResponseHandler
from src.connettori.base_connector import DatabaseConnector

logger = logging.getLogger(__name__)

class ChatService:
    """Servizio che gestisce la logica della chat"""
    def __init__(self, 
                 db: DatabaseConnector,
                 llm_manager,
                 metadata_retriever: DatabaseMetadataRetriever,
                 prompt_generator: PromptGenerator):
        """
        Inizializza il servizio chat
        
        Args:
            db: Istanza di un DatabaseConnector
            llm_manager: Gestore del modello LLM
            metadata_retriever: Retriever dei metadati del database
            prompt_generator: Generatore dei prompt
        """
        self.db = db
        if not self.db.connect():
            raise RuntimeError("Failed to connect to database")
            
        self.llm_manager = llm_manager
        self.metadata_retriever = metadata_retriever
        self.prompt_generator = prompt_generator
        self.response_handler = ResponseHandler(self.db)
    
    def process_message(self, message: str) -> dict:
        """ Elabora un messaggio dell'utente, interroga il modello e restituisce i risultati formattati"""
        logger.debug(f"Processing message: {message}")
        try:
            prompt = self.prompt_generator.generate_prompt(message)
            logger.debug(f"Generated prompt: {prompt}")

            llm_response = self.llm_manager.get_completion(prompt)
            logger.debug(f"LLM response: {llm_response}")

            results = self.response_handler.process_response(llm_response)
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