import os
import sys
from pathlib import Path

# Ottiene il percorso assoluto della directory del progetto
project_root = Path(__file__).resolve().parent

# Aggiunge la directory del progetto al Python path
sys.path.append(str(project_root))

# Imposta la working directory
os.chdir(project_root)

from flask import Flask
from src.web.routes import chat_bp

def create_app():
    # Calcola i percorsi assoluti per template e static
    template_dir = os.path.join(project_root, 'src', 'web', 'templates')
    static_dir = os.path.join(project_root, 'src', 'web', 'static')
    
    print(f"Template directory: {template_dir}")
    print(f"Static directory: {static_dir}")
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Abilita il debug per vedere eventuali errori
    app.config['DEBUG'] = True
    
    # Registra il blueprint
    app.register_blueprint(chat_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)