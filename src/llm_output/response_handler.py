import pandas as pd
from typing import Dict, Any
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
    
class ResponseHandler:
    """Processa la risposta generata dal LLM, formattandola ed estraendo query SQL e spiegazione + ci aggiunge i risultati dell'estrazione. 
    L'output di questa classe è ciò che vediamo in webapp in risposta alla nostra domanda"""
    
    def __init__(self, db): 
        self.db = db    
    
    def process_response(self, response: str) -> Dict[str, Any]:
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
            result = self.db.execute_query(parsed["query"])
            
            if result is None:
                return {
                    "success": False,
                    "error": "Errore nell'esecuzione della query",
                    "query": parsed["query"],
                    "explanation": parsed["explanation"]
                }

            columns, data = result  # spacchettamento del risultato
            df = pd.DataFrame(data, columns=columns)
            
            if df.empty:
                return {
                    "success": True,
                    "query": parsed["query"],
                    "explanation": parsed["explanation"],
                    "results": [],
                    "preview": []
                }
            
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
            
            # lista di possibili delimitatori di query SQL
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