import sys
import os
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))
os.chdir(project_root)

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hey-database-tutorial")


api_key = os.getenv("OPENAI_API_KEY")
db_pwd = os.getenv("POSTGRES_PWD")

from src.config.config_loader import ConfigLoader

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

from src.build.build_app_components import AppComponentsBuilder

app_components = AppComponentsBuilder(config).build()

from src.metadata.metadata_startup import (
    MetadataStartup,
    MetadataProcessor,
)

metadata_processor = MetadataProcessor(
    table_extractor=app_components.table_metadata_extractor,
    column_extractor=app_components.column_metadata_extractor,
    table_enhancer=app_components.table_metadata_enhancer,
    column_enhancer=app_components.column_metadata_enhancer,
)
metadata_manager = MetadataStartup(metadata_processor, app_components.cache)

metadata = metadata_manager.initialize_metadata()

from src.startup.vectorstore_startup import VectorStoreStartup

vector_store_startup = VectorStoreStartup(app_components.vector_store)
vector_store_startup.initialize(metadata)
