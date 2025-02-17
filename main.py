import os
import sys
import logging
from pathlib import Path

from flask import Flask
from src.config.config_loader import ConfigLoader
from src.build.build_app_components import AppComponentsBuilder
from src.services.chat_service import ChatService
from src.services.schema_service import SchemaService
from src.web.chat_routes import create_chat_routes
from src.web.schema_routes import create_schema_routes
from src.web.preview_routes import create_preview_routes
from src.metadata.metadata_startup import (
    MetadataStartup,
    MetadataProcessor,
)
from src.startup.vectorstore_startup import VectorStoreStartup

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("hey-database")


def create_app():
    project_root = Path(__file__).resolve().parent
    sys.path.append(str(project_root))
    os.chdir(project_root)

    template_dir = os.path.join(project_root, "src", "web", "templates")
    static_dir = os.path.join(project_root, "src", "web", "static")

    config = ConfigLoader.load_config(
        db_config_path=os.path.join(
            project_root, "configs", "DB_connections", "northwind_postgres.yaml"
        ),
        cache_config_path=os.path.join(
            project_root, "configs", "cache", "northwind_cache.yaml"
        ),
        sql_llm_config_path=os.path.join(
            project_root, "configs", "sql_llm", "openai_4o_mini.yaml"
        ),
        vector_store_config_path=os.path.join(
            project_root, "configs", "vector_store", "qdrant_northwind.yaml"
        ),
        prompt_config_path=os.path.join(project_root, "configs", "prompt.yaml"),
        metadata_config_path=os.path.join(project_root, "configs", "metadata_.yaml"),
        base_config_path=os.path.join(project_root, "configs", "base_config.yaml"),
    )

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # app.config["DEBUG"] = config.debug

    try:
        # Build all app components
        app_components = AppComponentsBuilder(config).build()

        # Initialization of metadata extractor and enhancer
        metadata_processor = MetadataProcessor(
            table_extractor=app_components.table_metadata_extractor,
            column_extractor=app_components.column_metadata_extractor,
            table_enhancer=app_components.table_metadata_enhancer,
            column_enhancer=app_components.column_metadata_enhancer,
        )
        metadata_startup = MetadataStartup(metadata_processor, app_components.cache)
        metadata = metadata_startup.initialize_metadata()

        vector_store_startup = VectorStoreStartup(app_components.vector_store)
        vector_store_startup.initialize(metadata)

        chat_service = ChatService(app_components.sql_llm)
        schema_service = SchemaService(metadata)

        # registra le routes
        create_chat_routes(app, chat_service)
        create_schema_routes(app, schema_service)
        create_preview_routes(app, app_components.db, app_components.metadata_retriever)

        # route principale
        @app.route("/")
        def index():
            """route principale che reindirizza alla chat"""
            from flask import redirect, url_for

            return redirect(url_for("chat.index"))

    except Exception as e:
        print(f"Failed to initialize service: {e}")
        raise

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000, use_reloader=False)
