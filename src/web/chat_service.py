from typing import List, Dict, Tuple, Optional
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
        """Elabora un messaggio dell'utente e restituisce i risultati formattati"""
        logger.debug(f"Processing message: {message}")
        try:
            # prima verifica match esatto nel vector store
            cached_result = self._get_cached_response(message)
            if cached_result:
                return cached_result
                
            # altrimenti genera una nuova risposta
            return self._generate_new_response(message)
            
        except Exception as e:
            logger.exception(f"Error processing message: {str(e)}")
            return {
                "success": False,
                "error": f"Errore nell'elaborazione del messaggio: {str(e)}"
            }
            
    def _get_cached_response(self, message: str) -> Optional[dict]:
        """Cerca una risposta cached nel vector store.
        
        Args:
            message: Messaggio dell'utente
            
        Returns:
            dict: Risultato cached se trovato, None altrimenti
        """
        if not self.vector_store:
            return None
            
        exact_match = self.vector_store.find_exact_match(message)
        if exact_match is None:
            logger.debug("No exact match found in vector store")
            return None
            
        logger.debug("Found exact match in vector store")
        stored_response = {
            "query": exact_match.sql_query.strip(),
            "explanation": exact_match.explanation
        }
        
        result = self.response_handler.process_response(stored_response)
        if result["success"]:
            result["from_vector_store"] = True
            result["original_question"] = message
            return result
            
        return None
    
    def _generate_new_response(self, message: str) -> dict:
        """Genera una nuova risposta usando il LLM.
        
        Args:
            message: Messaggio dell'utente
            
        Returns:
            dict: Risultato della query
        """
        # retrieve di contesto simile dallo store
        similar_tables, similar_queries = self._find_similar_content(message)
        
        # genera il prompt
        prompt = self.prompt_generator.generate_prompt(
            message,
            similar_tables=similar_tables,
            similar_queries=similar_queries
        )
        logger.debug(f"Generated prompt: {prompt}")
        
        # risposta del LLM
        llm_response = self.llm_manager.get_completion(prompt)
        if not llm_response:
            raise RuntimeError("LLM returned empty response")
        logger.debug(f"LLM response: {llm_response}")
        
        # restituzione dei risultati formattati
        return self._format_results(
            self.response_handler.process_response(llm_response),
            message
        )
        
        
    def _find_similar_content(self, message: str) -> Tuple[List[Dict], List[Dict]]:
        """Trova tabelle e query simili nel vector store rispetto al messaggio dell'utente.
        
        Args:
            message: Messaggio dell'utente
            
        Returns:
            Tuple[List[Dict], List[Dict]]: Liste di tabelle e query simili
        """
        similar_tables = []
        similar_queries = []
        
        if self.vector_store:
            # tabelle simili
            table_results = self.vector_store.search_similar_tables(message, limit=4)
            similar_tables = [{
                "table_name": t.metadata.table_name,
                "relevance_score": t.relevance_score,
                "row_count": t.metadata.row_count,
                "description": t.metadata.description,
                "columns": t.metadata.columns,
                "primary_keys": t.metadata.primary_keys,
                "foreign_keys": t.metadata.foreign_keys
            } for t in table_results]

            # query simili
            query_results = self.vector_store.search_similar_queries(message, limit=1)
            similar_queries = [{
                "question": q.question,
                "sql_query": q.sql_query,
                "explanation": q.explanation,
                "score": q.score,
                "positive_votes": q.positive_votes
            } for q in query_results]
            
        return similar_tables, similar_queries
        

    def _format_results(self, results: dict, original_message: str) -> dict:
        """Formatta i risultati nel formato finale atteso.
        
        Args:
            results: Risultati da formattare
            original_message: Messaggio originale dell'utente
            
        Returns:
            dict: Risultati formattati
        """
        if not results["success"]:
            return results
            
        if isinstance(results.get("results"), DataFrame):
            results["results"] = results["results"].to_dict('records')
        if isinstance(results.get("preview"), DataFrame):
            results["preview"] = results["preview"].to_dict('records')
            
        results["original_question"] = original_message
        results["from_vector_store"] = False
        
        return results
            
    def __del__(self):
        """Chiude le connessioni quando l'oggetto viene distrutto"""
        if hasattr(self, 'db'):
            self.db.close()
        if hasattr(self, 'vector_store'):
            self.vector_store.close()