import logging
from src.config.models.app import AppConfig
from src.services.chat_service import ChatService
from src.factories.builders.sql_agent_builder import SQLAgentBuilder

logger = logging.getLogger('hey-database')

class ServiceFactory:
    """Factory principale per la creazione dei servizi dell'applicazione"""

    @staticmethod
    def create_chat_service(app_config: AppConfig) -> ChatService:
        """Crea il servizio chat configurando l'SQLAgent sottostante"""
        try:
            sql_agent = (SQLAgentBuilder(app_config)
                         .build_database()
                         .build_llm()
                         .build_metadata_components()
                         .build_vector_store()
                         .build())

            # crea il service che wrappa l'agente
            return ChatService(sql_agent=sql_agent)

        except Exception as e:
            logger.exception("Failed to create chat service")
            raise