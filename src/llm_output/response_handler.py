import pandas as pd
import json
from typing import Dict, Any
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
    
class ResponseHandler:
    """Processa la risposta generata dal LLM, formattandola ed estraendo query SQL e spiegazione + ci aggiunge i risultati dell'estrazione. 
    L'output di questa classe è ciò che vediamo in webapp in risposta alla nostra domanda"""
    
    def __init__(self, db, schema): 
        self.db = db    
        self.schema = schema
    
    def process_response(self, response: str) -> Dict[str, Any]:
        """Process the LLM response and execute the SQL query.
        
        Args:
            response: JSON string from LLM containing query and explanation
            
        Returns:
            Dict with query results and metadata"""
            
        try:
            # estrae query e spiegazione
            parsed = self.parse_llm_response(response)
            
            if not parsed["query"]:
                return {
                    "success": False,
                    "error": "Query non trovata nella risposta",
                    "explanation": parsed.get("explanation", "")
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
        """Parse the JSON response from LLM.
        
        Args:
            response: JSON string from LLM
            
        Returns:
            Dict containing query and explanation
        """
        try:
            # Remove any potential markdown or extra text
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            
            return json.loads(response)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            return {
                "query": "",
                "explanation": f"Errore nel parsing della risposta JSON: {str(e)}"
            }