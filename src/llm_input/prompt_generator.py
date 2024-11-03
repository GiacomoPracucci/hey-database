import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class PromptGenerator:
    """Classe responsabile per la generazione dei prompt.
    Il prompt viene costruito estraendo metadati dallo schema che si deve interrogare, usando gli appositi retriever dei DB.
    """
    
    def __init__(self, metadata_retriever, schema_name: str, prompt_config):
        """Inizializza il gestore dei prompt.
        
        Args:
            metadata_retriever: Istanza dell'estrattore delle info del db (schema, tabelle, DDL)
        """
        
        self.metadata_retriever = metadata_retriever
        self.schema_name = schema_name
        self.prompt_config = prompt_config


    def generate_prompt(self, user_question: str) -> str:
        """Genera il prompt completo per il modello.
        
        Args:
            user_question (str): Domanda dell'utente
            include_sample_data (bool): Se includere dati di esempio
            max_sample_rows (int): Numero massimo di righe di esempio per tabella
            
        Returns:
            str: Prompt completo formattato"""
            
        prompt_parts = []
        
        # prompt template standard
        prompt_parts.append(f"""You are an SQL expert who helps convert natural language queries into SQL queries.
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
- Always insert schema name "{self.schema_name}" before the tables
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
        prompt_parts.append(self._format_metadata())
        # aggiunge dati di esempio (se richiesti)
        if self.prompt_config.include_sample_data:
            prompt_parts.append(self._format_sample_data(self.prompt_config.max_sample_rows))

        prompt_parts.append("\nRispondi in lingua Italiana.")
        prompt_parts.append("\nDOMANDA DELL'UTENTE:")
        prompt_parts.append(user_question)
        
        return "\n\n".join(prompt_parts)
    
    def _format_metadata(self) -> str:
        """Formatta la descrizione dello schema/tabelle in modo leggibile.
        Usando i metodi forniti dai retriever dei metadati.
        
        Returns:
            str: Descrizione formattata dello schema"""
        
        description = []
        description.append("Schema del Database:")
        
        for table_name, table_info in self.metadata_retriever.get_all_tables_metadata().items():
            description.append(f"\nTabella: {table_name} ({table_info.row_count} righe)")
            
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
        
        for table_name in self.metadata_retriever.get_all_tables_metadata():
            sample_data = self.metadata_retriever.get_sample_data(table_name, max_rows)
            if sample_data:
                samples.append(f"\n{table_name} (primi {len(sample_data)} record):")
                for row in sample_data:
                    samples.append(str(row))
        
        return "\n".join(samples)