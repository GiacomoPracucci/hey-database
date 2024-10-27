import os
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))
os.chdir(project_root)

from flask import Flask
from src.web.routes import chat_bp

def create_app():
    template_dir = os.path.join(project_root, 'src', 'web', 'templates')
    static_dir = os.path.join(project_root, 'src', 'web', 'static')
    
    print(f"Template directory: {template_dir}")
    print(f"Static directory: {static_dir}")
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    app.config['DEBUG'] = True
    
    app.register_blueprint(chat_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)