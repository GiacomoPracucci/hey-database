from openai import OpenAI
from typing import Union, List,  Any
import time
from tenacity import retry, stop_after_attempt, wait_exponential

class OpenAIHandler:
    """Classe per gestire le operazion con le API di OpenAI"""
    
    def __init__(self,
                 api_key: str,
                 embedding_model: str = "text-embedding-3-large",
                 chat_model: str = "gpt-4o"
                 ) -> None:
        """Inizializza il client OpenAI e configura i modelli da utilizzare.
        
        Args:
            api_key (str): OpenAI API key
            embedding_model (str): Nome del modello per gli embedding
            chat_model (str): Nome del modello per le chat
            max_retries (int): Numero massimo di tentativi in caso di errore
        """
        
        self.client = OpenAI(api_key=api_key)
        self.embedding_model = embedding_model
        self.chat_model = chat_model

    def _serialize_response(self, obj: Any) -> Any:
        """Serializza gli oggetti in formato JSON-compatibile.

        Args:
            obj: Oggetto da serializzare

        Returns:
            Any: Oggetto serializzato"""

        if hasattr(obj, 'keys'):  # Se è un dict-like object
            return {key: self._serialize_response(value) for key, value in dict(obj).items()}
        elif isinstance(obj, (list, tuple)):
            return [self._serialize_response(item) for item in obj]
        elif isinstance(obj, (int, float, str, bool, type(None))):
            return obj
        else:
            return str(obj)

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get_embedding(self, text: str) -> Union[List[float], None]:
        """Genera l'embedding per il testo fornito.
        
        Args:
            text (str): Testo di input
            
        Returns:
            Union[List[float], None]: Vettore dell'embedding o None in caso di errore"""
            
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            print(f"Errore nella generazione dell'embedding: {str(e)}")
            return None

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get_completion(self,
                       prompt: str,
                       system_prompt: str = "Sei un assistente utile ed accurato.",
                       temperature: float = 0.2,
                       max_tokens: int = 1000
                       ) -> Union[str, None]:
        """Ottiene una risposta dal modello di chat.
        
        Args:
            prompt (str): Prompt dell'utente
            system_prompt (str): Prompt di sistema per contestualizzare la conversazione
            temperature (float): Temperatura per la generazione (0-1)
            max_tokens (int): Numero massimo di token nella risposta
            
        Returns:
            Union[str, None]: Risposta del modello o None in caso di errore"""
            
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return self._serialize_response(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Errore nella generazione della risposta: {str(e)}")
            return None
        
    def get_embeddings_batch(self,
                             texts: List[str],
                             batch_size: int = 100
                             ) -> Union[List[List[float]], None]:
        """Genera embedding per una lista di testi in batch.
        
        Args:
            texts (List[str]): Lista di testi
            batch_size (int): Dimensione del batch
            
        Returns:
            Union[List[List[float]], None]: Lista di vettori embedding o None in caso di errore"""
        try:
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                batch_embeddings = [self._serialize_response(data.embedding) for data in response.data]
                embeddings.extend(batch_embeddings)
                
                # Piccola pausa per evitare rate limiting
                if i + batch_size < len(texts):
                    time.sleep(0.5)
                    
            return embeddings
            
        except Exception as e:
            print(f"Errore nella generazione degli embedding in batch: {str(e)}")
            return None
        
    def get_chat_stream(self,
                        prompt: str,
                        system_prompt: str = "Sei un assistente utile ed accurato.",
                        temperature: float = 0.2):
        """Genera una risposta in streaming dal modello di chat.
        
        Args:
            prompt (str): Prompt dell'utente
            system_prompt (str): Prompt di sistema
            temperature (float): Temperatura per la generazione
            
        Yields:
            str: Frammenti della risposta in streaming"""
        try:
            stream = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield self._serialize_response(chunk.choices[0].delta.content)
                    
        except Exception as e:
            print(f"Errore nello streaming della risposta: {str(e)}")
            yield None