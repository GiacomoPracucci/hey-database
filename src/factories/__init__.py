import logging
from src.config.models.app import AppConfig
from src.web.chat_service import ChatService
from src.factories.builders.chat import ChatServiceBuilder

logger = logging.getLogger('hey-database')

class ServiceFactory:
    """Factory principale per la creazione dei servizi dell'applicazione"""
    
    @staticmethod
    def create_chat_service(app_config: AppConfig) -> ChatService:
        """Crea un'istanza configurata del ChatService utilizzando il builder pattern"""
        try:
            return (ChatServiceBuilder(app_config)
                .build_database()
                .build_llm()
                .build_metadata_components()
                .build_vector_store()
                .build_prompt_generator()
                .build())
                
        except Exception as e:
            logger.exception("Failed to create chat service")
            raise