from abc import ABC, abstractmethod

class MetadataEnhancementStrategy(ABC):
    """Strategy pattern per determinare se fare l'enhancement dei metadati"""

    @abstractmethod
    def should_enhance(self) -> bool:
        """Determina se i metadati devono essere arricchiti

        Returns:
            bool: True se i metadati devono essere arricchiti, False altrimenti
        """
        pass