from flask import Blueprint, render_template, jsonify
import logging

from src.services.schema_service import SchemaService

logger = logging.getLogger("hey-database")
logger.setLevel(logging.DEBUG)


def create_schema_routes(app, schema_service: SchemaService):
    """
    Crea e configura le routes per la visualizzazione dello schema

    Args:
        app: Istanza Flask
        SchemaService: Istanza del metadata retriever per accedere alle informazioni dello schema
    """
    schema_bp = Blueprint("schema", __name__)

    @schema_bp.route("/")
    def view():
        """Pagina di visualizzazione dello schema del database"""
        logger.debug("Rendering schema page")
        return render_template("schema/index.html")

    @schema_bp.route("/api/metadata")
    def get_metadata():
        """
        Endpoint API che fornisce i metadati dello schema per la visualizzazione
        Restituisce la struttura completa del database incluse tabelle, colonne e relazioni
        """
        try:
            tables_metadata = schema_service.get_tables_metadata()
            columns_metadata = schema_service.get_columns_metadata()

            schema_data = {"tables": []}

            for table_name, enhanced_table_info in tables_metadata.items():
                
                table_data = {
                    "name": table_name,
                    "description": enhanced_table_info.description,
                    "columns": [],
                    "relationships": [],
                }

                # Recupera le colonne per questa tabella dai metadati colonna
                if table_name in columns_metadata:
                    table_columns = columns_metadata[table_name]
                    
                    # Aggiungi le informazioni di colonna
                    for col_name, col_info in table_columns.items():
                        column_data = {
                            "name": col_name,
                            "type": col_info.data_type,
                            "nullable": col_info.nullable,
                            "isPrimaryKey": col_info.is_primary_key,
                        }
                        table_data["columns"].append(column_data)

                # Estrai le relazioni (foreign keys) dai metadati della tabella
                for fk in enhanced_table_info.foreign_keys:
                    relationship = {
                        "fromColumns": fk["constrained_columns"],
                        "toTable": fk["referred_table"],
                        "toColumns": fk["referred_columns"],
                    }
                    table_data["relationships"].append(relationship)

                schema_data["tables"].append(table_data)

            return jsonify({"success": True, "data": schema_data})

        except Exception as e:
            logger.exception(f"Error retrieving schema metadata: {str(e)}")
            return jsonify(
                {
                    "success": False,
                    "error": f"Error retrieving schema metadata: {str(e)}",
                }
            ), 500

    # blueprint con prefisso URL
    app.register_blueprint(schema_bp, url_prefix="/schema")
