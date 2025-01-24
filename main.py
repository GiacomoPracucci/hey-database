import os
import sys
import logging
from pathlib import Path

from flask import Flask
from src.config.config_loader import ConfigLoader
from src.factories.builders.build_app_components import AppComponentsBuilder
from src.services.chat_service import ChatService
from src.services.schema_service import SchemaService
from src.web.chat_routes import create_chat_routes
from src.web.schema_routes import create_schema_routes
from src.web.preview_routes import create_preview_routes


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
            project_root, "configs", "DB_connection", "northwind_postgres.yaml"
        ),
        cache_config_path=os.path.join(
            project_root, "configs", "northwind_postgres.yaml"
        ),
        sql_llm_config_path=os.path.join(
            project_root, "configs", "cache", "sql_llm", "openai_4o_mini.yaml"
        ),
        prompt_config_path=os.path.join(project_root, "configs", "prompt.yaml"),
        metadata_config_path=os.path.join(project_root, "configs", "metadata_.yaml"),
        vector_store_config_path=os.path.join(
            project_root, "configs", "vector_store", "qdrant_northwind.yaml"
        ),
        base_config_path=os.path.join(project_root, "configs", "base_config.yaml"),
    )

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    app.config["DEBUG"] = config.debug

    try:
        # crea il servizio chat
        app_components = AppComponentsBuilder(config).build()
        chat_service = ChatService(app_components.sql_llm)
        schema_service = SchemaService(app_components.metadata_retriever)

        # registra le routes
        create_chat_routes(app, chat_service)
        create_schema_routes(app, schema_service)
        create_preview_routes(
            app, chat_service.sql_agent.db, chat_service.sql_agent.metadata_retriever
        )

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
