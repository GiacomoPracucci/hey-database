from pandas import DataFrame
import logging
from src.connettori.db_manager import DatabaseManager
from src.dbcontext.schema_context_manager import SchemaContextManager
from src.prompt.prompt_manager import PromptManager
from src.ollama_.ollama_manager import OllamaManager

logger = logging.getLogger(__name__)

class ChatService:
    """Classe che gestisce la logica del servizio di chat"""
    def __init__(self):
        
        self.db = DatabaseManager(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres",
            password="admin"
        )
        
        self.db.connect()
        
        self.ollama_manager = OllamaManager(
            base_url="http://localhost:11434",
            model="llama3.1"
        )
        
        self.schema_manager = SchemaContextManager(self.db.engine, schema="video_games")
        self.prompt_manager = PromptManager(self.schema_manager, self.db)
    
    def process_message(self, message: str) -> dict:
        logger.debug(f"Processing message: {message}")
        try:
            # Genera il prompt
            prompt = self.prompt_manager.generate_prompt(message)
            logger.debug(f"Generated prompt: {prompt}")
            
            # Ottieni la risposta dal modello
            llm_response = self.ollama_manager.get_completion(prompt)
            logger.debug(f"LLM response: {llm_response}")
            
            # Processa la query e ottieni i risultati
            results = self.prompt_manager.process_query(llm_response)
            logger.debug(f"Query results: {results}")
            
            # Converti il DataFrame in una lista di dizionari solo se è un DataFrame
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