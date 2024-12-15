from enum import Enum

class SupportedLanguage(Enum):
    """Per evitare che l'utente possa inserire in config lingue inestitenti, definiamo una lista di lingue supportate.
    Se la lingua inserita in config non è tra le presenti il LLM risponderà in automatico in Inglese"""
    
    ENGLISH = "english"
    MANDARIN = "mandarin"        
    HINDI = "hindi"              
    SPANISH = "spanish"          
    FRENCH = "french"            
    ARABIC = "arabic"            
    BENGALI = "bengali"          
    PORTUGUESE = "portuguese"    
    RUSSIAN = "russian"          
    URDU = "urdu"                
    INDONESIAN = "indonesian"    
    GERMAN = "german"            
    JAPANESE = "japanese"       
    SWAHILI = "swahili"          
    KOREAN = "korean"            
    TURKISH = "turkish"          
    VIETNAMESE = "vietnamese"    
    ITALIAN = "italian"          
    THAI = "thai"                
    PERSIAN = "persian"          
    POLISH = "polish"            
    DUTCH = "dutch"              
    GREEK = "greek"              
    CZECH = "czech"              
    SWEDISH = "swedish"          
    DANISH = "danish"            
    FINNISH = "finnish"          
    NORWEGIAN = "norwegian"      
    HEBREW = "hebrew"            
    ROMANIAN = "romanian"        
    HUNGARIAN = "hungarian"      
    MALAYALAM = "malayalam"      
    TAMIL = "tamil"              
    TELUGU = "telugu"            
    MARATHI = "marathi"          
    GUJARATI = "gujarati"        
    KANNADA = "kannada"          
    UKRAINIAN = "ukrainian"      
    TAGALOG = "tagalog"          
    MALAY = "malay"              

    @classmethod
    def get_default(cls) -> "SupportedLanguage":
        """Restituisce la lingua di default"""
        return cls.ENGLISH

    @classmethod
    def is_supported(cls, language: str) -> bool:
        """Verifica se la lingua in config è supportata"""
        return language.lower() in [lang.value for lang in cls]

    @classmethod
    def supported_languages(cls) -> list[str]:
        """Restituisce la lista delle lingue supportate"""
        return [lang.value for lang in cls]
    
    @classmethod
    def from_string(cls, language: str) -> "SupportedLanguage":
        """Converte una stringa nella corrispondente enum SupportedLanguage
        
        Args:
            language: Nome della lingua in inglese
        Returns:
            SupportedLanguage corrispondente o lingua di default se non supportata
        """
        try:
            return next(lang for lang in cls if lang.value == language.lower())
        except StopIteration:
            return cls.get_default()