from typing import Dict, Any
import yaml
import os
from dotenv import load_dotenv
from src.config.models import AppConfig, DatabaseConfig, LLMConfig

class ConfigLoader:
    @staticmethod
    def load_config(config_path: str) -> AppConfig:
        
        load_dotenv()
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
            
        config_data = ConfigLoader._resolve_env_vars(config_data)
        
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
        
        llm_config = LLMConfig(
            type=config_data['llm']['type'],
            api_key=config_data['llm'].get('api_key'),
            model=config_data['llm'].get('model'),
            base_url=config_data['llm'].get('base_url')            
        )
        
        return AppConfig(
            database=db_config,
            llm=llm_config,
            debug=config_data.get('debug', False)
        )
    
    @staticmethod
    def _resolve_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
        """Sostituisce i riferimenti alle variabili d'ambiente nel dizionario di configurazione"""
        if isinstance(config, dict):
            return {k: ConfigLoader._resolve_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [ConfigLoader._resolve_env_vars(v) for v in config]
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            env_var = config[2:-1]
            return os.getenv(env_var, '')
        return config