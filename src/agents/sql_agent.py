from typing import Optional, Dict, List, Tuple, Any

from src.connettori.connector import DatabaseConnector
from src.llm_handler.llm_handler import LLMHandler
from src.schema_metadata.metadata_retriever import DatabaseMetadataRetriever
from src.llm_output.response_handler import ResponseHandler
from src.store.vectorstore import VectorStore
from src.config.languages import SupportedLanguage
from src.agents.agent import Agent
from src.models.agent import SQLAgentResponse
from src.llm_output.parser import ResponseParser as parser
from src.llm_output.formatter import ResponseFormatter as formatter
from src.llm_output.sql_query_executor import SQLQueryExecutor as executor

import logging

logger = logging.getLogger("hey-database")


class SQLAgent(Agent):
    """Agente incaricato della generazione e dell'esecuzione di query SQL"""

    def __init__(
        self,
        db: DatabaseConnector,
        llm_manager: LLMHandler,
        metadata_retriever: DatabaseMetadataRetriever,
        schema_name: str,
        prompt_config: Any,
        vector_store: Optional[VectorStore] = None,
        language: SupportedLanguage = SupportedLanguage.get_default(),
    ):
        """Inizializza l'agente SQL

        Args:
            db: Connettore al database
            llm_manager: Gestore del modello di linguaggio
            metadata_retriever: Estrattore dei metadati del database
            schema_name: Nome dello schema del database
            prompt_config: Configurazione del prompt
            vector_store: Store per le query verificate (opzionale)
            language: Lingua per le risposte
        """
        self.db = db
        self.llm_manager = llm_manager
        self.metadata_retriever = metadata_retriever
        self.schema_name = schema_name
        self.prompt_config = prompt_config
        self.vector_store = vector_store
        self.language = language
        self.response_handler = ResponseHandler(self.db, schema_name)

    def run(self, message: str) -> SQLAgentResponse:
        """Esegue il task completo di generazione ed esecuzione query SQL + spiegazione
        Args:
            message: La domanda dell'utente
        Returns:
            SQLAgentResponse con i risultati o l'errore
        """
        logger.debug(f"Processing message: {message}\n")
        try:
            # 1. Verifichiamo se la risposta è già presente nel vector store
            cached_response = self._check_cache(message)
            if cached_response:
                return cached_response

            # retrieve di tabelle e query simili
            similar_tables, similar_queries = self._get_context(message)
            logger.debug(f"Similar tables: {similar_tables}\n")
            logger.debug(f"Similar queries: {similar_queries}\n")

            # costruisce ed esegue il prompt
            prompt = self.build_prompt(
                message, similar_tables=similar_tables, similar_queries=similar_queries
            )
            logger.debug(f"Generated prompt: {prompt}\n")

            llm_response = self.llm_manager.get_completion(prompt)
            if not llm_response:
                return SQLAgentResponse(
                    success=False,
                    error="Failed to get LLM response",
                    original_question=message,
                )
            logger.debug(f"LLM response: {llm_response}\n")

            parsed_response = parser.parse_llm_response(llm_response)
            query_result = executor.execute(parsed_response["query"], self.db)
            result = formatter.format_response(query_result, parsed_response)

            return SQLAgentResponse(
                success=result["success"],
                query=result.get("query"),
                explanation=result.get("explanation"),
                results=result.get("results"),
                preview=result.get("preview"),
                error=result.get("error"),
                original_question=message,
            )

        except Exception as e:
            logger.exception(f"Error in SQL agent: {str(e)}")
            return SQLAgentResponse(
                success=False, error=str(e), original_question=message
            )

    def build_prompt(
        self,
        message: str,
        similar_tables: Optional[List[Dict]] = None,
        similar_queries: Optional[List[Dict]] = None,
    ) -> str:
        """Costruisce il prompt per il LLM
        Args:
            message: Domanda dell'utente
            similar_tables: Lista di tabelle rilevanti
            similar_queries: Lista di query simili precedenti
        Returns:
            str: Prompt formattato
        """
        prompt_parts = []

        # template base
        prompt_parts.append(f"""You are an SQL expert who helps convert natural language queries into SQL queries.
Your task is:
1. Generate a valid SQL query that answers the user's question
2. Provide a brief explanation of the results

You must respond with a JSON object in the following format:
{{
    "query": "YOUR SQL QUERY HERE",
    "explanation": "Brief explanation of what the query does and what results to expect"
}}

Important:
- Always insert schema name "{self.schema_name}" before the tables
- Do not include comments in the SQL query
- The query must be executable
- Use the table DDL information to ensure correct column names and types
- Follow the foreign key relationships when joining tables
- If you do not have the necessary information to respond or if the requested data does not appear to be in the DB:
    - Explain in the explanation field why the request cannot be fulfilled
    - generate a simple SQL query to extract generic data from a single table (with a limit 5)
    - Explain what the sample data shows

Response must be valid JSON - do not include any other text or markdown formatting.
        """)

        # aggiunge tabelle rilevanti al prompt
        if similar_tables:
            prompt_parts.append("\nRelevant Tables:")
            for table_info in similar_tables:
                prompt_parts.append(self._format_table_metadata(table_info))
                if (
                    self.prompt_config.include_sample_data
                ):  # se in config abbiamo specificato che vogliamo records di esempio
                    sample_data = self._get_sample_data(
                        table_info["table_name"], self.prompt_config.max_sample_rows
                    )
                    if sample_data:
                        prompt_parts.append(sample_data)

        # aggiunge query simili a quella fatta dall'utente al prompt
        if similar_queries:
            prompt_parts.append("\nSimilar Questions and Queries:")
            for query_info in similar_queries:
                prompt_parts.append(self._format_similar_query(query_info))

        # Lingua e domanda
        prompt_parts.append(f"\nAnswer in {self.language.value} language.")
        prompt_parts.append("\nUSER QUESTION:")
        prompt_parts.append(message)

        return "\n\n".join(prompt_parts)

    def _check_cache(self, message: str) -> Optional[SQLAgentResponse]:
        """Verifica se esiste una risposta cached nel vector store
        Args:
            message: Domanda dell'utente
        Returns:
            SQLAgentResponse se trovata, None altrimenti
        """
        if not self.vector_store:
            return None
        # cerchiamo una corrispondenza esatta nel vector store per la domanda fatta
        exact_match = self.vector_store.find_exact_match(message)
        if exact_match is None:
            logger.debug("No exact match found in vector store")
            return None

        logger.debug("Found exact match in vector store")
        # prendiamo query SQL e spiegazione
        stored_response = {
            "query": exact_match.sql_query.strip(),
            "explanation": exact_match.explanation,
        }
        # e le formattiamo
        result = self.response_handler.process_response(stored_response)
        # restituiamo quindi la risposta cached
        if result["success"]:
            return SQLAgentResponse(
                success=True,
                query=result["query"],
                explanation=result["explanation"],
                results=result.get("results"),
                preview=result.get("preview"),
                from_vector_store=True,
                original_question=message,
            )
        # se la risposta non è stata processata correttamente, restituiamo None
        return None

    def _get_context(self, message: str) -> Tuple[List[Dict], List[Dict]]:
        """Recupera tabelle e query simili dal vector store
        Args:
            message: Domanda dell'utente
        Returns:
            Tuple[List[Dict], List[Dict]]: Tabelle e query simili
        """
        similar_tables = []
        similar_queries = []

        if self.vector_store:
            # tabelle simili
            table_results = self.vector_store.search_similar_tables(message, limit=4)
            similar_tables = [
                {
                    "table_name": t.metadata.table_name,
                    "relevance_score": t.relevance_score,
                    "row_count": t.metadata.row_count,
                    "description": t.metadata.description,
                    "columns": t.metadata.columns,
                    "primary_keys": t.metadata.primary_keys,
                    "foreign_keys": t.metadata.foreign_keys,
                }
                for t in table_results
            ]

            # query simili
            query_results = self.vector_store.search_similar_queries(message, limit=1)
            similar_queries = [
                {
                    "question": q.question,
                    "sql_query": q.sql_query,
                    "explanation": q.explanation,
                    "score": q.score,
                    "positive_votes": q.positive_votes,
                }
                for q in query_results
            ]

        return similar_tables, similar_queries

    @staticmethod
    def _format_table_metadata(table_info: Dict) -> str:
        """Formatta i metadati di una tabella per il prompt
        Args:
            table_info: Informazioni sulla tabella
        Returns:
            str: Metadati formattati
        """
        description = [
            f"\nTable: {table_info['table_name']} ({table_info['row_count']} rows)",
            f"Relevance Score: {table_info['relevance_score']:.2f}",
            f"Description: {table_info['description']}",
            "Columns:",
        ]

        for col in table_info["columns"]:
            nullable = "NULL" if col["nullable"] else "NOT NULL"
            description.append(f"- {col['name']} ({col['type']}) {nullable}")

        if table_info["primary_keys"]:
            description.append(f"Primary Keys: {', '.join(table_info['primary_keys'])}")

        if table_info["foreign_keys"]:
            description.append("Foreign Keys:")
            for fk in table_info["foreign_keys"]:
                description.append(
                    f"- {', '.join(fk['constrained_columns'])} -> "
                    f"{fk['referred_table']}({', '.join(fk['referred_columns'])})"
                )

        return "\n".join(description)

    @staticmethod
    def _format_similar_query(query_info: Dict) -> str:
        """Formatta una query simile per il prompt
        Args:
            query_info: Informazioni sulla query
        Returns:
            str: Query formattata
        """
        return f"""
Similar Question (Score: {query_info["score"]:.2f}, Positive Votes: {query_info["positive_votes"]}):
Q: {query_info["question"]}
SQL: {query_info["sql_query"]}
Explanation: {query_info["explanation"]}"""

    def _get_sample_data(self, table_name: str, max_rows: int = 3) -> str:
        """Recupera e formatta dati di esempio da una tabella
        Args:
            table_name: Nome della tabella
            max_rows: Numero massimo di righe
        Returns:
            str: Dati di esempio formattati
        """
        sample_data = self.metadata_retriever.get_sample_data(table_name, max_rows)
        if not sample_data:
            return ""

        formatted_samples = [
            f"\nSample Data for {table_name} (First {len(sample_data)} records):"
        ]

        for row in sample_data:
            formatted_row = "{\n"
            for key, value in row.items():
                formatted_row += f"    {key}: {value},\n"
            formatted_row += "}"
            formatted_samples.append(formatted_row)

        return "\n".join(formatted_samples)

    def handle_feedback(self, question: str, sql_query: str, explanation: str) -> bool:
        """Gestisce il feedback positivo dell'utente
        Args:
            question: Domanda originale
            sql_query: Query SQL generata
            explanation: Spiegazione fornita

        Returns:
            bool: True se il feedback è stato salvato con successo
        """
        if not self.vector_store:
            logger.warning("Vector store is not enabled")
            return False

        return self.vector_store.handle_positive_feedback(
            question=question, sql_query=sql_query, explanation=explanation
        )

    def __del__(self):
        """Cleanup when the agent is destroyed"""
        if hasattr(self, "db"):
            self.db.close()
