from abc import ABC, abstractmethod
from typing import Dict, List, Optional,Any

class Agent(ABC):
    """Classe base per gli agenti"""
    def run(self):
        """Esegue il task assegnato all'agente"""
        pass