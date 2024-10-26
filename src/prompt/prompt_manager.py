from typing import Dict, Optional, List, Any
from dataclasses import dataclass

class PromptManager:
    """Classe responsabile per la gestione e generazione dei prompt."""
    
    def __init__(self, schema_manager, db_manager):
        """Inizializza il gestore dei prompt.
        
        Args:
            schema_manager (SchemaContextManager): Istanza del gestore dello schema"""
        self.schema_manager = schema_manager
        self.db_manager = db_manager
    
    def _format_schema_description(self) -> str:
        """Formatta la descrizione dello schema in modo leggibile.
        
        Returns:
            str: Descrizione formattata dello schema"""
        
        description = []
        description.append("Schema del Database:")
        
        for table_name, table_info in self.schema_manager.get_all_tables().items():
            description.append(f"\nTabella: {table_name} ({table_info.row_count} righe)")
            
            # Descrizione colonne
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

After the query, provide:
Explanation: [Brief explanation of what the query does and what results to expect]
        """)
        
        # Schema del database
        prompt_parts.append(self._format_schema_description())
        
        # Dati di esempio (se richiesti)
        if include_sample_data:
            prompt_parts.append(self._format_sample_data(max_sample_rows))
        
        # Domanda dell'utente
        prompt_parts.append("\nDOMANDA DELL'UTENTE:")
        prompt_parts.append(user_question)
        
        return "\n\n".join(prompt_parts)

    def parse_llm_response(self, response: str) -> Dict[str, str]:
        """ Analizza la risposta del modello e estrae la query SQL e la spiegazione.
        
        Args:
            response (str): Risposta dal modello
            
        Returns:
            Dict[str, str]: Dizionario con query e spiegazione"""
        try:
            # Estrae la query SQL (assume che sia racchiusa in ```sql ... ```)
            sql_start = response.find("```sql")
            sql_end = response.find("```", sql_start + 6)
            
            if sql_start == -1 or sql_end == -1:
                # Fallback: cerca solo la query senza il tag sql
                sql_start = response.find("```")
                sql_end = response.find("```", sql_start + 3)
            
            query = response[sql_start:sql_end].strip()
            query = query.replace("```sql", "").replace("```", "").strip()
            
            # Rimuove i commenti SQL
            query_lines = query.split('\n')
            query_lines = [line.strip() for line in query_lines if line.strip() and not line.strip().startswith('--')]
            query = '\n'.join(query_lines)
            
            # Estrae la spiegazione (tutto ciò che segue dopo "Explanation:")
            explanation_start = response.find("Explanation:")
            explanation = response[explanation_start:].strip() if explanation_start != -1 else ""
            
            return {
                "query": query,
                "explanation": explanation.replace("Explanation:", "").strip()
            }
        except Exception as e:
            print(f"Errore nel parsing della risposta: {e}")
            return {
                "query": "",
                "explanation": "Errore nel parsing della risposta del modello."
            }

    def process_query(self, response: str) -> Dict[str, Any]:
        """Analizza la risposta del modello, estrae la query SQL, la esegue e fornisce i risultati.
        
        Args:
            response (str): Risposta dal modello
            
        Returns:
            Dict[str, Any]: Dizionario con query, spiegazione e risultati"""
        try:
            # Estrae query e spiegazione
            parsed = self.parse_llm_response(response)
            
            if not parsed["query"]:
                return {
                    "success": False,
                    "error": "Query non trovata nella risposta",
                    "explanation": parsed["explanation"]
                }
            
            # Esegue la query
            df = self.db_manager.execute_query(parsed["query"])
            
            if df is None:
                return {
                    "success": False,
                    "error": "Errore nell'esecuzione della query",
                    "query": parsed["query"],
                    "explanation": parsed["explanation"]
                }
            
            # Converti sempre i DataFrame in liste di dizionari
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
