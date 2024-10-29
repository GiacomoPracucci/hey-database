from flask import Blueprint, render_template, request, jsonify
import logging
import os
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from src.web.chat_service import ChatService
from src.ollama_.ollama_manager import OllamaManager
from src.openAI.openai_handler import OpenAIManager
from src.connettori.postgres import PostgresManager

chat_bp = Blueprint('chat', __name__)

db = PostgresManager(
    host="localhost",
    port="5432",
    database="postgres",
    user="postgres",
    password=os.getenv("DB_PWD")
)

#self.llm_manager = OllamaManager(
#    base_url="http://localhost:11434",
#    model="llama3.1"
#)

llm_manager = OpenAIManager(
    api_key=os.getenv("OPENAI_API_KEY"),
    embedding_model="text-embedding-3-large",
    chat_model="gpt-4o"
)

chat_service = ChatService(db, llm_manager)

@chat_bp.route('/')
def index():
    """ Index page """
    logger.debug("Rendering index page")
    return render_template('index.html')

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    """ Chat endpoint """
    logger.debug("Received chat request")
    try:
        data = request.get_json() # prende i dati in formato JSON dalla richiesta
        logger.debug(f"Request data: {data}")
        
        if not data:
            logger.error("No JSON data received")
            return jsonify({"success": False, "error": "No data received"}), 400
        
        message = data.get('message', '') # prende il messaggio dalla richiesta
        logger.debug(f"Message received: {message}")
        
        if not message:
            logger.error("No message in request")
            return jsonify({"success": False, "error": "Messaggio mancante"}), 400
            
        logger.debug("Processing message with chat service")
        response = chat_service.process_message(message)
        logger.debug(f"Chat service response: {response}")
        
        return jsonify(response)
        
    except Exception as e:
        logger.exception(f"Error in chat endpoint: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500