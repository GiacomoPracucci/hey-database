from typing import Any, Dict, List, Optional
from src.config.languages import SupportedLanguage
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PromptGenerator:
    """Classe responsabile per la generazione dei prompt.
    Il prompt viene costruito estraendo metadati dallo schema che si deve interrogare, usando gli appositi retriever dei DB.
    """
    
    def __init__(self, metadata_retriever, schema_name: str, prompt_config, language: SupportedLanguage = SupportedLanguage.get_default()):
        """Inizializza il gestore dei prompt.
        
        Args:
            metadata_retriever: Istanza dell'estrattore delle info del db (schema, tabelle, DDL)
            schema_name: Nome dello schema del database
            prompt_config: Configurazione del prompt
            language: Lingua in cui il modello dovrebbe rispondere
        """
        
        self.metadata_retriever = metadata_retriever
        self.schema_name = schema_name
        self.prompt_config = prompt_config
        self.language = language


    def generate_prompt(self, 
                        user_question: str,
                        similar_tables: Optional[List[Dict[str, Any]]] = None,
                        similar_queries: Optional[List[Dict[str, Any]]] = None
                        ) -> str:
        """Genera il prompt completo per il modello.
        
        Args:
            user_question: Domanda dell'utente
            similar_tables: Lista di dizionari con struttura:
                {
                    "table_name": str,
                    "relevance_score": float,
                    "row_count": int,
                    "description": str,
                    "columns": List[Dict],
                    "primary_keys": List[str],
                    "foreign_keys": List[Dict]
                }
            similar_queries: Lista di dizionari con struttura:
                {
                    "question": str,
                    "sql_query": str,
                    "explanation": str,
                    "score": float,
                    "positive_votes": int
                }
        """
            
        prompt_parts = []
        
        # prompt template standard
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
        
        # Aaggiunge le tabelle rilevanti e i metadati associati
        if similar_tables:
            prompt_parts.append("\nRelevant Tables:")
            for table_info in similar_tables:
                prompt_parts.append(self._format_table_metadata(table_info))
                if self.prompt_config.include_sample_data:
                    sample_data = self._sample_table_data(
                        table_info["table_name"],
                        self.prompt_config.max_sample_rows
                    )
                    if sample_data:
                        prompt_parts.append(sample_data)
        
        # esempi di query simili
        if similar_queries:
            prompt_parts.append("\nSimilar Questions and Queries:")
            for query_info in similar_queries:
                prompt_parts.append(self._format_similar_query(query_info))

        prompt_parts.append(f"\nAnswer in {self.language.value} language.")
        prompt_parts.append("\nUSER QUESTION:")
        prompt_parts.append(user_question)
        
        return "\n\n".join(prompt_parts)

    
    def _format_table_metadata(self, table_info: Dict[str, Any]) -> str:
        """Formatta i metadati di una singola tabella."""
        description = []
        description.append(f"\nTabella: {table_info['table_name']} ({table_info['row_count']} righe)")
        description.append(f"Relevance Score: {table_info['relevance_score']:.2f}")
        description.append(f"Description: {table_info['description']}")
        
        description.append("Colonne:")
        for col in table_info["columns"]:
            nullable = "NULL" if col["nullable"] else "NOT NULL"
            description.append(f"- {col['name']} ({col['type']}) {nullable}")
        
        if table_info["primary_keys"]:
            description.append(f"Chiavi Primarie: {', '.join(table_info['primary_keys'])}")
        
        if table_info["foreign_keys"]:
            description.append("Foreign Keys:")
            for fk in table_info["foreign_keys"]:
                description.append(
                    f"- {', '.join(fk['constrained_columns'])} -> "
                    f"{fk['referred_table']}({', '.join(fk['referred_columns'])})"
                )
        
        return "\n".join(description)

    def _format_similar_query(self, query_info: Dict[str, Any]) -> str:
        """Formatta una query simile per l'inclusione nel prompt."""
        return f"""
Similar Question (Score: {query_info['score']:.2f}, Positive Votes: {query_info['positive_votes']}):
Q: {query_info['question']}
SQL: {query_info['sql_query']}
Explanation: {query_info['explanation']}"""
    
    
    def _sample_table_data(self, table_name: str, max_rows: int = 3) -> str:
        """Formatta i dati di esempio per una singola tabella.
        
        Args:
            table_name: Nome della tabella da cui estrarre i dati
            max_rows: Numero massimo di righe da mostrare
            
        Returns:
            str: Dati di esempio formattati o stringa vuota se non ci sono dati
        """
        sample_data = self.metadata_retriever.get_sample_data(table_name, max_rows)
        if not sample_data:
            return ""
            
        formatted_samples = []
        formatted_samples.append(f"\nSample Data for {table_name} (First {len(sample_data)} records):")
        
        # formattazione dei risultati
        for row in sample_data:
            # formatta la riga come dizionario ma con indentazione e a capo
            formatted_row = "{\n"
            for key, value in row.items():
                formatted_row += f"    {key}: {value},\n"
            formatted_row += "}"
            formatted_samples.append(formatted_row)
        
        return "\n".join(formatted_samples)