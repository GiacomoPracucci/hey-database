from flask import Blueprint, render_template, request, jsonify
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def create_routes(app, chat_service):
    """ Crea e configuraz le routes dell'app
    
    Args:
    app: Istanza Flask
    chat_service: Istanza di ChatService già configurata
    """
    chat_bp = Blueprint('chat', __name__)
    
    @chat_bp.route('/')
    def index():
        """Index Page"""
        logger.debug("Rendering index page")
        return render_template('index.html')
    
    @chat_bp.route('/api/chat', methods=['POST'])
    def chat():
        """Chat endpoint"""
        logger.debug("Received chat request")
        try:
            data = request.get_json()
            logger.debug(f"Request data: {data}")
            
            if not data:
                logger.error("No JSON data received")
                return jsonify({"success": False, "error": "No data received"}), 400
            
            message = data.get('message', '')
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

    app.register_blueprint(chat_bp)
    
    return app