import os
import logging
from sqlalchemy import create_engine, text
from datetime import datetime

from src.config.config_loader import ConfigLoader
from src.config.factory import ServiceFactory
from src.config.models.app import AppConfig
from src.llm_handler.openai_handler import OpenAIHandler
from src.config.models.metadata import EnhancedTableMetadata
from src.config.models.vector_store import TablePayload, QueryPayload
from src.connettori.postgres import PostgresManager

from src.embedding.openai_embedding import OpenAIEmbedding
from src.schema_metadata.postgres_metadata_retriever import PostgresMetadataRetriever

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def setup_test_database():
    """Crea un database di test con alcune tabelle usando il nostro PostgresManager"""
    
    # Crea connessione usando il nostro manager
    db_manager = PostgresManager(
        host="localhost",
        port="5432",
        database="postgres",
        user="postgres",
        password="admin"
    )
    
    if not db_manager.connect():
        raise RuntimeError("Failed to connect to database")
    
    try:
        with db_manager.engine.connect() as conn:
            # Crea schema
            conn.execute(text("DROP SCHEMA IF EXISTS test_schema CASCADE"))
            conn.execute(text("CREATE SCHEMA test_schema"))
            
            # Crea tabelle di test
            conn.execute(text("""
                CREATE TABLE test_schema.products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    price DECIMAL(10,2),
                    category_id INTEGER
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE test_schema.categories (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    description TEXT
                )
            """))
            
            conn.execute(text("""
                ALTER TABLE test_schema.products 
                ADD CONSTRAINT fk_category 
                FOREIGN KEY (category_id) 
                REFERENCES test_schema.categories(id)
            """))
            
            # Inserisci dati di esempio
            conn.execute(text("""
                INSERT INTO test_schema.categories (name, description)
                VALUES 
                    ('Electronics', 'Electronic devices and accessories'),
                    ('Books', 'Books and e-books'),
                    ('Clothing', 'Apparel and accessories')
            """))
            
            conn.execute(text("""
                INSERT INTO test_schema.products (name, price, category_id)
                VALUES 
                    ('Smartphone', 699.99, 1),
                    ('Laptop', 1299.99, 1),
                    ('Python Programming', 49.99, 2),
                    ('T-shirt', 19.99, 3)
            """))
            
            conn.commit()
        
        return db_manager
    
    except Exception as e:
        logger.error(f"Failed to setup test database: {str(e)}")
        db_manager.close()
        raise
def test_metadata_enhancement(llm_handler, metadata_retriever):
    """Testa l'enhancement dei metadati"""
    logger.info("Testing metadata enhancement...")
    
    # Crea enhancer
    metadata_enhancer = ServiceFactory.create_metadata_enhancer(llm_handler)
    
    # Ottieni metadati base
    base_metadata = metadata_retriever.get_all_tables_metadata()
    logger.info(f"Retrieved base metadata for {len(base_metadata)} tables")
    
    # Enhance metadati
    enhanced_metadata = metadata_enhancer.enhance_all_metadata(base_metadata)
    logger.info("Enhanced metadata generated")
    
    # Verifica risultati
    for table_name, metadata in enhanced_metadata.items():
        logger.info(f"\nTable: {table_name}")
        logger.info(f"Description: {metadata.description}")
        logger.info(f"Keywords: {metadata.keywords}")
        logger.info(f"Importance score: {metadata.importance_score}")
    
    return enhanced_metadata

def test_vector_store(config, enhanced_metadata):
    """Testa le funzionalità del vector store"""
    logger.info("\nTesting vector store...")
    
    # Crea vector store
    vector_store = ServiceFactory.create_vector_store(config.vector_store)
    
    # Inizializza con metadati
    logger.info("Initializing vector store with metadata...")
    success = vector_store.initialize(enhanced_metadata)
    assert success, "Failed to initialize vector store"
    
    # Test ricerca tabelle rilevanti
    test_queries = [
        "Show me all products and their prices",
        "List categories and their descriptions",
        "Find expensive electronics"
    ]
    
    for query in test_queries:
        logger.info(f"\nTesting query: {query}")
        relevant_tables = vector_store.search_similar_tables(query)
        logger.info(f"Found {len(relevant_tables)} relevant tables:")
        for result in relevant_tables:
            logger.info(f"Table: {result.table_name}")
            logger.info(f"Score: {result.relevance_score}")
            logger.info(f"Matched keywords: {result.matched_keywords}")
    
    # Test feedback e query caching
    test_query = {
        'question': "What are the most expensive products?",
        'sql_query': "SELECT name, price FROM test_schema.products ORDER BY price DESC LIMIT 5",
        'explanation': "This query finds the top 5 most expensive products."
    }
    
    logger.info("\nTesting query feedback...")
    success = vector_store.handle_positive_feedback(
        question=test_query['question'],
        sql_query=test_query['sql_query'],
        explanation=test_query['explanation']
    )
    assert success, "Failed to handle feedback"
    
    # Test ricerca query simili
    logger.info("\nTesting similar query search...")
    similar_queries = vector_store.search_similar_queries("Show expensive items")
    for query in similar_queries:
        logger.info(f"Question: {query.question}")
        logger.info(f"Score: {query.score}")
        logger.info(f"Votes: {query.positive_votes}")
    
    return vector_store

from src.config.models.app import AppConfig
from src.config.models.db import DatabaseConfig
from src.config.models.llm import LLMConfig
from src.config.models.vector_store import VectorStoreConfig
from src.config.models.embedding import EmbeddingConfig
from src.config.languages import SupportedLanguage
from src.config.models.prompt import PromptConfig

def main():
    """Test principale che verifica l'intero flusso"""
    try:
        # Setup database di test
        logger.info("Setting up test database...")
        db_manager = setup_test_database()
        
        # Crea le configurazioni usando i modelli corretti
        db_config = DatabaseConfig(
            type='postgres',
            host='localhost',
            port='5432',
            database='postgres',
            user='postgres',
            password='admin',
            schema='test_schema'
        )
        
        llm_config = LLMConfig(
            type='openai',
            api_key=os.getenv('OPENAI_API_KEY'),
            model='gpt-4',
            language=SupportedLanguage.get_default()
        )
        
        embedding_config = EmbeddingConfig(
            type='openai',
            model_name='text-embedding-3-small',
            api_key=os.getenv('OPENAI_API_KEY')
        )
        
        vector_store_config = VectorStoreConfig(
            enabled=True,
            type='qdrant',
            collection_name='test_collection',
            path='./test_vector_store',
            url = None,
            embedding=embedding_config
        )
        
        prompt_config = PromptConfig(
            include_sample_data=True,
            max_sample_rows=3
        )
        
        # Crea AppConfig con i modelli corretti
        config = AppConfig(
            database=db_config,
            llm=llm_config,
            prompt=prompt_config,
            vector_store=vector_store_config,
            debug=True
        )
        
        # Crea servizi base
        llm = ServiceFactory.create_llm_handler(config.llm)
        metadata_retriever = ServiceFactory.create_metadata_retriever(config.database, db_manager)
        
        # Test enhancement metadati
        enhanced_metadata = test_metadata_enhancement(llm, metadata_retriever)
        
        # Test vector store
        vector_store = test_vector_store(config, enhanced_metadata)
        
        logger.info("\nAll tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise
    finally:
        # Cleanup
        if 'db_manager' in locals():
            db_manager.close()
        if 'vector_store' in locals():
            vector_store.close()

if __name__ == "__main__":
    main()