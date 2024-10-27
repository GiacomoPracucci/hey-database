from flask import Blueprint, render_template, request, jsonify
from src.web.chat_service import ChatService
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)
chat_service = ChatService()

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