from typing import Dict, Any, Optional
import yaml
import os
from dotenv import load_dotenv
from src.config.languages import SupportedLanguage
from src.config.models.app import AppConfig
from src.config.models.db import DatabaseConfig
from src.config.models.llm import LLMConfig
from src.config.models.prompt import PromptConfig
from src.config.models.vector_store import VectorStoreConfig
from src.config.models.embedding import EmbeddingConfig
from src.config.models.cache import CacheConfig
from src.config.models.metadata import MetadataConfig

import logging

logger = logging.getLogger('hey-database')


class ConfigLoader:
    
    @staticmethod
    def _resolve_refs(config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Risolve i riferimenti interni nel dizionario di configurazione"""
        if isinstance(config, dict):
            return {k: ConfigLoader._resolve_refs(v, context) for k, v in config.items()}
        elif isinstance(config, list):
            return [ConfigLoader._resolve_refs(v, context) for v in config]
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            var_name = config[2:-1]
            # prima cerca nelle variabili di contesto
            if var_name in context:
                return context[var_name]
            # poi nelle variabili d'ambiente
            return os.getenv(var_name, '')
        return config
    
    
    @staticmethod
    def load_config(config_path: str) -> AppConfig:
        
        load_dotenv()
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)

        context = {
            'db_schema': config_data['database']['schema']
        }
            
        config_data = ConfigLoader._resolve_refs(config_data, context)
        
        db_config = DatabaseConfig(
            type=config_data['database']['type'],
            host=config_data['database']['host'],
            port=config_data['database']['port'],
            database=config_data['database']['database'],
            user=config_data['database']['user'],
            password=config_data['database']['password'],
            schema=config_data['database']['schema'],
            warehouse=config_data['database'].get('warehouse'),
            account=config_data['database'].get('account'),
            role=config_data['database'].get('role')
        )

        # load cache configuration
        cache_config = CacheConfig(
            enabled=config_data.get('cache', {}).get('enabled', False),
            directory=config_data.get('cache', {}).get('directory'),
            ttl_hours=config_data.get('cache', {}).get('ttl_hours', 24)
        )
        
        language_str = config_data['llm'].get('language', SupportedLanguage.get_default().value)
        if not SupportedLanguage.is_supported(language_str):
            logger.warning(
                f"Lingua '{language_str}' non supportata. "
                f"Lingue supportate: {', '.join(SupportedLanguage.get_supported_languages())}. "
                f"Verrà utilizzata la lingua di default ({SupportedLanguage.get_default().value})"
            )
        
        llm_config = LLMConfig(
            type=config_data['llm']['type'],
            api_key=config_data['llm'].get('api_key'),
            model=config_data['llm'].get('model'),
            base_url=config_data['llm'].get('base_url'),
            language=SupportedLanguage.from_string(language_str)            
        )

        prompt_config = PromptConfig(
            include_sample_data=config_data.get('prompt', {}).get('include_sample_data', True),
            max_sample_rows=config_data.get('prompt', {}).get('max_sample_rows', 3)
        )
        
        vector_store_config = ConfigLoader._load_vector_store_config(config_data)

        # Resolve ${db_schema} in cache directory if needed
        if cache_config.directory and '${db_schema}' in cache_config.directory:
            cache_config.directory = cache_config.directory.replace('${db_schema}', context['db_schema'])
            
        metadata_config = MetadataConfig(
            retrieve_distinct_values=config_data.get('metadata', {}).get('retrieve_distinct_values', False),
            max_distinct_values=config_data.get('metadata', {}).get('max_distinct_values', 100)
        )

        return AppConfig(
            database=db_config,
            llm=llm_config,
            prompt=prompt_config,
            cache = cache_config,
            metadata=metadata_config,
            vector_store=vector_store_config,
            debug=config_data.get('debug', False)
        )
    
    @staticmethod
    def _load_vector_store_config(config_data: dict) -> Optional[VectorStoreConfig]:
        """Carica la configurazione del vector store se presente"""
        if 'vector_store' not in config_data:
            return None
        
        vs_data = config_data['vector_store']
        
        if not vs_data.get('enabled', False):
            return None
        
        # contesto per la sostituzione delle variabili nel config.yaml
        context = {
            'db_schema': config_data['database']['schema']
        }
        path = vs_data.get('path')
        if path:
            path = path.replace('${db_schema}', context['db_schema'])
            
        collection_name = vs_data['collection_name'].replace('${db_schema}', context['db_schema'])

        if 'embedding' not in vs_data:
            raise ValueError("Missing embedding configuration in vector_store config")
            
        embedding_data = vs_data['embedding']
        embedding_config = EmbeddingConfig(
            type=embedding_data['type'],
            model_name=embedding_data['model_name'],
            api_key=embedding_data.get('api_key')  # opzionale, richiesto solo per OpenAI
        )
                    
        return VectorStoreConfig(
            enabled=vs_data.get('enabled', False),
            type=vs_data['type'],
            collection_name=collection_name,
            path=path,      
            url=vs_data.get('url'),
            embedding=embedding_config,
            api_key=vs_data.get('api_key'),
            batch_size=vs_data.get('batch_size', 100),
        )
