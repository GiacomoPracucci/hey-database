from flask import Blueprint, jsonify
import logging

logger = logging.getLogger('hey-database')
logger.setLevel(logging.DEBUG)

def create_preview_routes(app, db):
    """ Crea e configura le routes per la preview dei dati
    
    Args:
        app: Istanza Flask
        db: Istanza DatabaseConnector per l'accesso al database
    """
    preview_bp = Blueprint('preview', __name__)
    schema = db.schema
    
    @preview_bp.route('/api/tables/<table_name>/preview')
    def get_table_preview(table_name):
        """Endpoint che fornisce una preview dei dati di una tabella
        
        Args:
            table_name (str): Nome della tabella di cui ottenere la preview
            
        Returns:
            JSON response con:
            - success: bool indicante il successo dell'operazione
            - data: lista di dizionari contenenti i dati della preview
            - error: messaggio di errore (solo se success=False)
        """
        try:
            logger.debug(f"Retrieving preview data for table: {schema}.{table_name}")
            
            # Costruisce la query con lo schema corretto
            query = f"SELECT * FROM {schema}.{table_name} LIMIT 10"
            
            result = db.execute_query(query)
            
            if not result:
                logger.debug(f"No data available for table {table_name}")
                return jsonify({
                    "success": True,
                    "data": []
                })
                
            # Spacchetta i risultati
            columns, rows = result
            
            # Converte i risultati in una lista di dizionari
            preview_data = [
                dict(zip(columns, row))
                for row in rows
            ]
            
            logger.debug(f"Preview data retrieved successfully for table {table_name}")
            
            return jsonify({
                "success": True,
                "data": preview_data
            })
            
        except Exception as e:
            logger.exception(f"Error retrieving preview data for table {table_name}: {str(e)}")
            
            return jsonify({
                "success": False,
                "error": f"Failed to retrieve preview data: {str(e)}"
            }), 500
    
    # Registra il blueprint con il prefisso /preview
    app.register_blueprint(preview_bp, url_prefix='/preview')
    
    return app