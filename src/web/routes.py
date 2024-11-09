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

    @chat_bp.route('/api/feedback', methods=['POST'])
    def feedback():
        """Endpoint per gestire il feedback positivo dell'utente"""
        try:
            
            logger.debug("Ricevuta richiesta di feedback")
            data = request.get_json()
            logger.debug(f"Dati ricevuti: {data}")
            
            if not data or not all(key in data for key in ['question', 'sql_query', 'explanation']):
                logger.error("Dati mancanti nella richiesta")
                return jsonify({"success": False, "error": "Dati mancanti"}), 400
                
            success = chat_service.vector_store.handle_positive_feedback(
                question=data['question'],
                sql_query=data['sql_query'],
                explanation=data['explanation']
            )
            
            logger.debug(f"Feedback processato con successo: {success}")
            
            if success:
                return jsonify({"success": True})
            else:
                return jsonify({"success": False, "error": "Errore nel salvataggio del feedback"}), 500
                
        except Exception as e:
            logger.exception(f"Errore nell'endpoint feedback: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    @chat_bp.route('/api/debug/vectorstore', methods=['GET'])
    def debug_vectorstore():
        """Endpoint di debug per vedere il contenuto del vector store"""
        if chat_service.vector_store:
            chat_service.vector_store.debug_list_all_entries()
        return jsonify({"message": "Check logs for vector store content"})
    
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