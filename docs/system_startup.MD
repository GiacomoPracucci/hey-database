# System Initialization Flow

The system follows a layered initialization approach, ensuring all components are properly configured and data is loaded in the correct order. Here's how the system bootstraps itself:

## 1. `Configuration Loading`

- Loads configuration from YAML files for all system components
- Includes database connections, cache settings, LLM settings, and vector store parameters
- Validates configuration and resolves environment variables

## 2. `Components Building`
The AppComponentsBuilder creates and configures core system components:
- Database connector (Postgres, Vertica, etc.)
- Vector store client (Qdrant)
- LLM handler (OpenAI, Anthropic, etc.)
- Cache system
- Metadata extractors and enhancers

## 3. `Metadata Processing`
Handled by MetadataStartup and MetadataProcessor:
1. Checks for valid cached metadata
2. If no valid cache:
    - Extracts base metadata from database schema
    - Enhances metadata with LLM-generated descriptions
    - Caches the processed metadata
3. Returns fully processed metadata for tables and columns

## 4. `Vector Store Initialization`
Final step handled by VectorStoreStartup:
1. Initializes or verifies vector store collection:
    - Checks collection existence
    - Validates vector dimensions match embedding model
    - Creates collection if needed
2. Syncs current metadata to vector store:
    - Updates table nodes with table metadata and embeddings
    - Updates column nodes with column metadata and embeddings
    - Uses upsert operations to ensure consistency

The vector store acts as a searchable knowledge graph of the database schema, enabling semantic search and relationship exploration.  

This initialization ensures all components are properly configured and data is consistently synchronized across the system.