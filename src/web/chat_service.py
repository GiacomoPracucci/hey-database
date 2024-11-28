from pandas import DataFrame
import logging
from src.schema_metadata.base_metadata_retriever import DatabaseMetadataRetriever
from src.llm_input.prompt_generator import PromptGenerator
from src.llm_output.response_handler import ResponseHandler
from src.connettori.base_connector import DatabaseConnector
from src.store.base_vectorstore import VectorStore
from src.llm_handler.base_llm_handler import LLMHandler
logger = logging.getLogger('hey-database')

class ChatService:
    """Servizio che gestisce la logica della chat"""
    def __init__(self, 
                 db: DatabaseConnector,
                 llm_manager: LLMHandler,
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
            exact_match = None
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
            
            # ricerca di tabelle e query rilevanti
            similar_tables = []
            similar_queries = []
            if self.vector_store:
                table_results = self.vector_store.search_similar_tables(message, limit=3)
                similar_tables = [{
                    "table_name": t.metadata.table_name,
                    "relevance_score": t.relevance_score,
                    "row_count": t.metadata.row_count,
                    "description": t.metadata.description,
                    "columns": t.metadata.columns,
                    "primary_keys": t.metadata.primary_keys,
                    "foreign_keys": t.metadata.foreign_keys
                } for t in table_results]

                query_results = self.vector_store.search_similar_queries(message, limit=3)
                similar_queries = [{
                    "question": q.question,
                    "sql_query": q.sql_query,
                    "explanation": q.explanation,
                    "score": q.score,
                    "positive_votes": q.positive_votes
                } for q in query_results]

            # genera il prompt includendo tabelle e query simili
            prompt = self.prompt_generator.generate_prompt(
                message,
                similar_tables=similar_tables,
                similar_queries=similar_queries
            )
            
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