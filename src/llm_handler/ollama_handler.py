import requests
from typing import Union, List, Dict, Any, Generator
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from src.llm_handler.llm_handler import LLMHandler


class OllamaHandler(LLMHandler):
    """Classe per gestire le operazioni con i modelli Ollama locali"""
    
    def __init__(self,
                 base_url: str = "http://localhost:11434",
                 model: str = "llama3.2"
                 ) -> None:
        """Inizializza il client Ollama.
        
        Args:
            base_url (str): URL base per l'API Ollama
            model (str): Nome del modello da utilizzare
            max_retries (int): Numero massimo di tentativi in caso di errore"""
        
        self.base_url = base_url.rstrip('/')
        self.model = model

    def _make_request(self,
                      endpoint: str,
                      method: str = "POST",
                      data: Dict = None
                      ) -> Union[Dict, None]:
        """Metodo interno per effettuare richieste HTTP all'API di Ollama.
        
        Args:
            endpoint (str): Endpoint dell'API
            method (str): Metodo HTTP
            data (Dict): Dati da inviare
            
        Returns:
            Union[Dict, None]: Risposta dell'API o None in caso di errore"""
        
        try:
            url = f"{self.base_url}/{endpoint}"
            
            if method == "POST":
                response = requests.post(url, json=data)
            else:
                response = requests.get(url)
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Errore nella richiesta API: {str(e)}")
            return None
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get_completion(self,
                       prompt: str,
                       system_prompt: str = None,
                       temperature: float = 0.2,
                       max_tokens: int = 1000,
                       ) -> Union[str, Generator[str, None, None], None]:
        """Ottiene una risposta dal modello.
        
        Args:
            prompt (str): Prompt dell'utente
            system_prompt (str): Prompt di sistema opzionale
            temperature (float): Temperatura per la generazione
            max_tokens (int): Numero massimo di token nella risposta
            top_p (float): Parametro top_p per il sampling
            stream (bool): Se True, restituisce la risposta in streaming
            
        Returns:
            Union[str, Generator[str, None, None], None]: Risposta del modello o generator per lo streaming"""
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if system_prompt:
            data["system"] = system_prompt
            
        response = self._make_request("api/generate", data=data)
        return response.get("response") if response else None
    
    
    def get_chat_stream(self,
                       prompt: str,
                       system_prompt: str = None,
                       temperature: float = 0.2
                       ) -> Generator[str, None, None]:
        """Get streaming response from Ollama API"""
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature
            }
        }
        
        if system_prompt:
            data["system"] = system_prompt
            
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if "response" in json_response:
                        yield json_response["response"]
                        
        except Exception as e:
            print(f"Error in response streaming: {str(e)}")
            yield None
            
            
    def list_models(self) -> Union[List[Dict], None]:
        """ Ottiene la lista dei modelli disponibili localmente """
        
        response = self._make_request("api/tags", method="GET")
        return response.get("models") if response else None    
    
    def pull_model(self, model_name: str) -> bool:
        """ Scarica un nuovo modello.
        
        Args:
            model_name (str): Nome del modello da scaricare
            
        Returns:
            bool: True se il download ha successo, False altrimenti """
        data = {
            "name": model_name
        }
        
        response = self._make_request("api/pull", data=data)
        return response is not None
    
    def get_model_info(self, model_name: str = None) -> Union[Dict, None]:
        """Ottiene informazioni su un modello specifico."""
        
        model = model_name or self.model
        data = {
            "name": model
        }
        
        return self._make_request("api/show", data=data)
    
    def set_model(self, model_name: str):
        """Cambia il modello corrente"""
        self.model = model_name