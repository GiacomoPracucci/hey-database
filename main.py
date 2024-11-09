import os
import sys
import logging
import tempfile
import uuid
from pathlib import Path

from flask import Flask
from src.config.config_loader import ConfigLoader
from src.config.factory import ServiceFactory 
from src.web.routes import create_routes


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
    
    template_dir = os.path.join(project_root, 'src', 'web', 'templates')
    static_dir = os.path.join(project_root, 'src', 'web', 'static')
    config_path = os.path.join(project_root, 'config.yaml')
    
    config = ConfigLoader.load_config(config_path)
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    app.config['DEBUG'] = config.debug
    
    try:
        chat_service = ServiceFactory.create_chat_service(config)
        create_routes(app, chat_service)
    except Exception as e:
        print(f"Failed to initialize service: {e}")
        raise
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000, use_reloader=False)