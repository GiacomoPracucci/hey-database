import os
import sys
import logging
from pathlib import Path
from flask_cors import CORS
from flask import Flask, jsonify
from src.config.config_loader import ConfigLoader
from src.factories import ServiceFactory 
from src.backend.chat_routes import create_chat_routes
from src.backend.schema_routes import create_schema_routes

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('hey-database')

def create_app():
    project_root = Path(__file__).resolve().parent
    sys.path.append(str(project_root))
    os.chdir(project_root)
    
    config_path = os.path.join(project_root, 'configs', 'northwind_postgres.yaml')
    config = ConfigLoader.load_config(config_path)
    
    app = Flask(__name__)
    CORS(app)  # Configurazione CORS semplice ma sufficiente per sviluppo
    
    app.config['DEBUG'] = config.debug
    
    try:
        chat_service = ServiceFactory.create_chat_service(config)
        create_chat_routes(app, chat_service)
        create_schema_routes(app, chat_service.sql_agent.metadata_retriever)
        
    except Exception as e:
        logger.error(f"Failed to initialize service: {e}")
        raise
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000, use_reloader=False)