from flask import Blueprint, render_template, jsonify
import logging

logger = logging.getLogger('hey-database')
logger.setLevel(logging.DEBUG)

def create_schema_routes(app, metadata_retriever):
    """Crea e configura le routes per la visualizzazione dello schema
    
    Args:
        app: Istanza Flask
        metadata_retriever: Istanza del metadata retriever per accedere alle informazioni dello schema
    """
    schema_bp = Blueprint('schema', __name__)
    
    @schema_bp.route('/')
    def view():
        """Pagina di visualizzazione dello schema del database"""
        logger.debug("Rendering schema page")
        return render_template('schema/index.html')
    
    @schema_bp.route('/api/metadata')
    def get_metadata():
        """Endpoint API che fornisce i metadati dello schema per la visualizzazione
        Restituisce la struttura completa del database incluse tabelle, colonne e relazioni
        """
        try:
            # Recupera i metadati dal retriever
            tables_metadata = metadata_retriever.get_all_tables_metadata()
            
            # Formatta i dati per il frontend
            schema_data = {
                "tables": []
            }
            
            for table_name, table_info in tables_metadata.items():
                table_data = {
                    "name": table_name,
                    "columns": [],
                    "relationships": []
                }
                
                # colonne
                for col in table_info.columns:
                    column_data = {
                        "name": col["name"],
                        "type": col["type"],
                        "nullable": col["nullable"],
                        "isPrimaryKey": col["name"] in table_info.primary_keys
                    }
                    table_data["columns"].append(column_data)
                
                # relazioni (foreign keys)
                for fk in table_info.foreign_keys:
                    relationship = {
                        "fromColumns": fk["constrained_columns"],
                        "toTable": fk["referred_table"],
                        "toColumns": fk["referred_columns"]
                    }
                    table_data["relationships"].append(relationship)
                
                schema_data["tables"].append(table_data)
            
            return jsonify({"success": True, "data": schema_data})
            
        except Exception as e:
            logger.exception(f"Error retrieving schema metadata: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Error retrieving schema metadata: {str(e)}"
            }), 500
    
    # blueprint con prefisso URL
    app.register_blueprint(schema_bp, url_prefix='/schema')