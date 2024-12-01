from abc import ABC, abstractmethod
from typing import Dict, List, Optional,Any

class Agent(ABC):
    """Classe base per gli agenti"""
    def run(self, input_data: Optional[Any] = None) -> Any:
        """Esegue il task assegnato all'agente"""
        pass

    def build_prompt(self, input_data: Optional[Any] = None) -> str:
        """Costruisce il prompt per l'agente"""
        pass