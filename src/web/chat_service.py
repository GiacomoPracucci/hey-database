from pandas import DataFrame
import logging
from src.dbcontext.base_metadata_retriever import DatabaseMetadataRetriever
from src.llm_input.prompt_generator import PromptGenerator
from src.llm_output.response_handler import ResponseHandler
from src.connettori.base_connector import DatabaseConnector
from src.store.base_vectorstore import VectorStore
logger = logging.getLogger('hey-database')

class ChatService:
    """Servizio che gestisce la logica della chat"""
    def __init__(self, 
                 db: DatabaseConnector,
                 llm_manager,
                 metadata_retriever: DatabaseMetadataRetriever,
                 prompt_generator: PromptGenerator,
                 vector_store: VectorStore = None):
        """
        Inizializza il servizio chat
        
        Args:
            db: Istanza di un DatabaseConnector
            llm_manager: Gestore del modello LLM
            metadata_retriever: Retriever dei metadati del database
            prompt_generator: Generatore dei prompt
            vector_store: Store per le query verificate (opzionale)
            self.vector_store = vector_store
        """
        self.db = db
        if not self.db.connect():
            raise RuntimeError("Failed to connect to database")
            
        self.llm_manager = llm_manager
        self.metadata_retriever = metadata_retriever
        self.prompt_generator = prompt_generator
        self.vector_store = vector_store
        self.response_handler = ResponseHandler(self.db, self.metadata_retriever.schema)
    
    def process_message(self, message: str) -> dict:
        """ Elabora un messaggio dell'utente, interroga il modello e restituisce i risultati formattati"""
        logger.debug(f"Processing message: {message}")
        try:
            # prima verifica se abbiamo una risposta simile nel vector store
            if self.vector_store:
                exact_match = self.vector_store.find_exact_match(message)
                
            if exact_match is not None: 
                logger.debug("Found exact match in vector store")
                #  dizionario nel formato atteso dal ResponseHandler
                stored_response = {
                    "query": exact_match.sql_query.strip(),
                    "explanation": exact_match.explanation
                }
                
                # ResponseHandler per processare la risposta cached
                result = self.response_handler.process_response(stored_response)
                if result["success"]:
                    result["from_vector_store"] = True
                    result["original_question"] = message
                    return result
                    
                logger.debug("No exact match found, using LLM")
                
            # se non troviamo una risposta simile o il vector store non è configurato,
            # procediamo con la generazione normale
            prompt = self.prompt_generator.generate_prompt(message)
            logger.debug(f"Generated prompt: {prompt}")

            llm_response = self.llm_manager.get_completion(prompt)
            
            logger.debug(f"LLM response: {llm_response}")
            
            logger.debug(f"Raw LLM response: {llm_response}")
        
            if not llm_response:
                raise RuntimeError("LLM returned empty response")

            results = self.response_handler.process_response(llm_response)
            logger.debug(f"Query results: {results}")

            if results["success"]:
                if isinstance(results.get("results"), DataFrame):
                    results["results"] = results["results"].to_dict('records')
                if isinstance(results.get("preview"), DataFrame):
                    results["preview"] = results["preview"].to_dict('records') 
                results["original_question"] = message
                results["from_vector_store"] = False
            
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
        if hasattr(self, 'vector_store'):
            self.vector_store.close()