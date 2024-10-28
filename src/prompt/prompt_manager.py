from typing import Dict, Optional, List, Any
from dataclasses import dataclass
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PromptManager:
    """Classe responsabile per la gestione e generazione dei prompt."""
    
    def __init__(self, schema_manager, db_manager):
        """Inizializza il gestore dei prompt.
        
        Args:
            schema_manager (SchemaContextManager): Istanza del gestore dello schema
            db_manager (DatabaseManager): Istanza del gestore di connessione e query verso il DB"""
        
        self.schema_manager = schema_manager
        self.db_manager = db_manager

    def _get_table_ddl(self, table_name: str) -> str:
        """Recupera il DDL di una tabella specifica.
        Args:
            table_name (str): Nome della tabella
        Returns:
            str: DDL della tabella"""
        try:
            query = f"""
            SELECT pg_get_tabledef('{self.schema_manager.schema}.{table_name}'::regclass);
            """ # funzione creata in postgres per ottenere il ddl di una tabella
            df = self.db_manager.execute_query(query)
            if df is not None and not df.empty:
                return df.iloc[0, 0]
            return ""
        except Exception as e:
            logger.error(f"Errore nel recupero del DDL per {table_name}: {str(e)}")
            return ""

    
    def _format_schema_description(self) -> str:
        """Formatta la descrizione dello schema in modo leggibile.
        
        Returns:
            str: Descrizione formattata dello schema"""
        
        description = []
        description.append("Schema del Database:")
        
        for table_name, table_info in self.schema_manager.get_all_tables().items():
            description.append(f"\nTabella: {table_name} ({table_info.row_count} righe)")

            ddl = self._get_table_ddl(table_name)
            if ddl:
                description.append("DDL:")
                description.append(ddl)
            
            description.append("Colonne:")
            for col in table_info.columns:
                nullable = "NULL" if col["nullable"] else "NOT NULL"
                description.append(f"- {col['name']} ({col['type']}) {nullable}")
            
            if table_info.primary_keys:
                description.append(f"Chiavi Primarie: {', '.join(table_info.primary_keys)}")
            
            if table_info.foreign_keys:
                description.append("Foreign Keys:")
                for fk in table_info.foreign_keys:
                    description.append(
                        f"- {', '.join(fk['constrained_columns'])} -> "
                        f"{fk['referred_table']}({', '.join(fk['referred_columns'])})"
                    )
        
        return "\n".join(description)
    
    def _format_sample_data(self, max_rows: int = 3) -> str:
        """Formatta i dati di esempio di tutte le tabelle.
        
        Args:
            max_rows (int): Numero massimo di righe per tabella
            
        Returns:
            str: Dati di esempio formattati
        """
        samples = []
        samples.append("\nEsempi di Dati:")
        
        for table_name in self.schema_manager.get_all_tables():
            sample_data = self.schema_manager.get_sample_data(table_name, max_rows)
            if sample_data:
                samples.append(f"\n{table_name} (primi {len(sample_data)} record):")
                for row in sample_data:
                    samples.append(str(row))
        
        return "\n".join(samples)
    
    def generate_prompt(self,
                        user_question: str,
                        include_sample_data: bool = True,
                        max_sample_rows: int = 3
                        ) -> str:
        """Genera il prompt completo per il modello.
        
        Args:
            user_question (str): Domanda dell'utente
            include_sample_data (bool): Se includere dati di esempio
            max_sample_rows (int): Numero massimo di righe di esempio per tabella
            
        Returns:
            str: Prompt completo formattato"""
            
        prompt_parts = []
        
        # Sistema prompt
        prompt_parts.append("""You are an SQL expert who helps convert natural language queries into SQL queries.
Your task is:
1. Generate a valid SQL query that answers the user's question
2. Provide a brief explanation of the results

Response format:
```sql
SELECT column_names
FROM table_names
WHERE conditions;
```

Important:
- Always insert schema name "video_games" before the tables
- Do not include comments in the SQL query
- The query must be executable
- Use the table DDL information to ensure correct column names and types
- Follow the foreign key relationships when joining tables

After the query, provide:
Explanation: [Brief explanation of what the query does and what results to expect]

if you do not have the necessary information to respond or if the requested data does not appear to be in the DB, 
generate a simple SQL query to extract generic data from a single table (with a limit 5) and inform the user in the explanation 
that you cannot fulfill their request, concisely explaining the reason.
        """)
        
        # aggiunge info sullo schema del database
        prompt_parts.append(self._format_schema_description())
        # aggiunge dati di esempio (se richiesti)
        if include_sample_data:
            prompt_parts.append(self._format_sample_data(max_sample_rows))

        prompt_parts.append("\nRispondi in lingua Italiana.")
        prompt_parts.append("\nDOMANDA DELL'UTENTE:")
        prompt_parts.append(user_question)
        
        return "\n\n".join(prompt_parts)
    
    
    def process_query(self, response: str) -> Dict[str, Any]:
        """Analizza la risposta del modello, estrae la query SQL, la esegue e fornisce i risultati.
        
        Args:
            response (str): Risposta dal modello
            
        Returns:
            Dict[str, Any]: Dizionario con query, spiegazione e risultati"""
        try:
            # estrae query e spiegazione
            parsed = self.parse_llm_response(response)
            
            if not parsed["query"]:
                return {
                    "success": False,
                    "error": "Query non trovata nella risposta",
                    "explanation": parsed["explanation"]
                }
            
            # esegue la query
            df = self.db_manager.execute_query(parsed["query"])
            
            if df is None:
                return {
                    "success": False,
                    "error": "Errore nell'esecuzione della query",
                    "query": parsed["query"],
                    "explanation": parsed["explanation"]
                }
            
            # converti sempre i DataFrame in liste di dizionari
            results_dict = df.to_dict('records')
            preview_dict = df.head().to_dict('records')
            
            return {
                "success": True,
                "query": parsed["query"],
                "explanation": parsed["explanation"],
                "results": results_dict,
                "preview": preview_dict
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Errore nel processing della query: {str(e)}",
                "query": parsed.get("query", ""),
                "explanation": parsed.get("explanation", "")
            }    
    

    def parse_llm_response(self, response: str) -> Dict[str, str]:
        """ Analizza la risposta del modello e estrae la query SQL e la spiegazione.
        
        Args:
            response (str): Risposta dal modello
            
        Returns:
            Dict[str, str]: Dizionario con query e spiegazione
        """
        try:
            response = response.strip().replace('\r\n', '\n')
            
            # Lista di possibili delimitatori di query SQL
            sql_markers = [
                ("```sql", "```"),  # Markdown SQL
                ("```", "```"),     # Markdown generico
                ("SELECT", ";"),    # Query SQL diretta
                ("WITH", ";"),      # Per query con CTE
                ("select", ";"),    # Case insensitive
                ("with", ";")       # Case insensitive per CTE
            ]
            
            query = self._search_sql_query(response, sql_markers)
        
            if not query:
                raise ValueError("Nessuna query SQL valida trovata nella risposta")
                
            query = self._clean_sql_query(query)
            explanation = self._search_explanation(response)
            
            return {
                "query": query,
                "explanation": explanation
            }
            
        except Exception as e:
            logger.error(f"Errore nel parsing della risposta LLM: {str(e)}")
            return {
                "query": "",
                "explanation": f"Errore nel parsing della risposta: {str(e)}"
            }
    
    def _search_sql_query(self, response, sql_markers) -> str:
        """cerca la query usando i vari delimitatori """
        query = None
        for start_marker, end_marker in sql_markers:
            start_idx = response.lower().find(start_marker.lower())
            if start_idx != -1:
                # se troviamo un marker di inizio
                start_pos = start_idx + len(start_marker)
                if end_marker == "```":
                    end_idx = response.find(end_marker, start_pos)
                    if end_idx != -1:
                        query = response[start_pos:end_idx]
                        break
                else:  # Per i casi SELECT/WITH
                    # cerca il primo ; dopo la posizione di start
                    end_idx = response.find(end_marker, start_idx)
                    if end_idx != -1:
                        query = response[start_idx:end_idx + 1]
                        break
        return query

    def _clean_sql_query(self, query: str) -> str:
        """Pulisce e valida una query SQL.
        
        Args:
            query (str): Query SQL grezza
            
        Returns:
            str: Query SQL pulita e validata
            
        Raises:
            ValueError: Se la query non è valida"""
        
        # rimuove i marker di codice se presenti
        query = query.replace("```sql", "").replace("```", "").strip()
        
        # rimuove i commenti
        query_lines = []
        for line in query.split('\n'):
            line = line.strip()
            if line and not line.startswith('--'):
                # Rimuove i commenti inline
                comment_idx = line.find('--')
                if comment_idx != -1:
                    line = line[:comment_idx].strip()
                if line:
                    query_lines.append(line)
        
        query = ' '.join(query_lines)
        
        # validazione base
        if not any(keyword in query.lower() for keyword in ['select', 'with']):
            raise ValueError("La query non contiene SELECT o WITH")
            
        if 'video_games.' not in query:
            # aggiungi automaticamente lo schema se mancante
            query = query.replace('FROM ', 'FROM video_games.')
            
        return query
    
    def _search_explanation(self, response):
        """Estrae la spiegazione della query SQL dalla risposta del LLM"""
        explanation = ""
        explanation_markers = ["explanation:", "spiegazione:", "this query"]
        for marker in explanation_markers:
            exp_idx = response.lower().find(marker)
            if exp_idx != -1:
                explanation = response[exp_idx:].strip()
                break
        return explanation