# Hey, Database! Natural Language SQL Assistant

An intelligent assistant that enables natural language interaction with your database, powered by Large Language Models.  
Ask questions in plain language and get SQL queries, detailed explanations, and formatted results.

[heydatabase.webm](https://github.com/user-attachments/assets/0bf67ffd-fd4b-4d39-8ef6-be8381e95738)

## ✨ Core Features

### Natural Language Understanding

- Translate natural language questions into SQL queries
- Get detailed explanations of how queries work
- Multi-language support for questions and responses

### Intelligent Schema Understanding

- Automatic database schema metadata extraction
- Smart metadata enhancement using LLMs to describe table purposes
- Interactive schema browser with relationship visualization

### Advanced Query Intelligence

- Semantic search to find relevant tables for your questions
- Column-level semantic matching in development (find specific columns that match your intent)
- Real-time query previews and result explanations

### Customizable RAG Recipes

- Modular Retrieval-Augmented Generation (RAG) pipelines
- Configure specialized recipes for different query patterns
- Mix and match strategies for query understanding, retrieval, and prompt building
- Create domain-specific recipes optimized for different use cases

### Self-Learning System

- Learns from successful queries through user feedback

## 🚀 AI-Powered Core

- Modular LLM integration (OpenAI, Anthropic, Local Models)
- Sophisticated prompt engineering for accurate SQL generation
- Vector store-based semantic memory system
- Metadata enhancement through AI understanding
- Pluggable RAG strategies with dependency injection

## Privacy & Storage Considerations

The system offers flexible storage options to match your privacy and performance requirements:

**Vector Store Options**

- Local Qdrant Storage:

  - Complete data privacy with all vectors stored locally
  - Faster response times for subsequent queries
  - Higher disk space requirements
  - Ideal for sensitive data environments

- Cloud Qdrant Storage:
  - Reduced local storage footprint
  - Managed infrastructure
  - Requires data transmission to cloud
  - Better for distributed setups

**Metadata Caching**

- Enabled:

  - Faster schema introspection
  - Reduced database load
  - Local storage of schema metadata
  - Better performance for large schemas

- Disabled:
  - No local metadata storage
  - Real-time schema information
  - Lower local resource usage
  - Increased database queries

**Sample Data in Prompts**

- Enabled (include_sample_data: true):

  - Sample rows are sent to LLM provider
  - More context-aware responses
  - Increased token usage

- Disabled (include_sample_data: false):
  - Only schema metadata are sent to LLM provider
  - Reduced token consumption

Choose the configuration that best balances your privacy requirements, performance needs, and resource constraints.

## 📋 Prerequisites

- Python 3.8+
- One of the supported databases:
  - PostgreSQL
  - MySQL 8.0+
  - Snowflake account
- OpenAI API key (if using OpenAI) or Ollama instance (if using local models)
- Vector store requirements (optional):
  - Qdrant (local or cloud)
  - HuggingFace or OpenAI for embeddings

## 🔧 Setup

1. Clone the repository:

```
git clone <repository-url>
cd hey-database
```

2. Create and activate a virtual environment:

```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Set up environment variables:

```
cp .env.example .env
```

Edit .env and add your:

- Database credentials
- OpenAI API key (if using OpenAI)
- Ollama endpoint (if using Ollama)

5. Configure the application (config.yaml):

   ```yaml
   database:
     type: postgres # or mysql or snowflake or vertica
     host: ...
     port: ...
     database: ...
     user: ...
     password: ...
     schema: ...

   llm:
     type: openai # or ollama
     api_key: ${OPENAI_API_KEY}
     model: gpt-4o

   vector_store:
     enabled: true
     type: qdrant
     collection_name: ${db_schema}_store
     path: ./data/${db_schema}_store
     batch_size: 100
     embedding:
       type: huggingface # or openai
       model_name: sentence-transformers/multi-qa-MiniLM-L6-cos-v1
       # api_key: ${OPENAI_API_KEY}  # required for OpenAI embeddings
   ```

6. Configure RAG recipes (optional):
  Create YAML files in the configs/rag_recipes directory to define custom RAG recipes:

      ```yaml
      name: "custom_recipe"
      description: "A custom RAG recipe for financial queries"
      default: true  # Set as default recipe 

      query_understanding:
        type: "PassthroughQueryUnderstanding"
        params: {}

      retrieval:
        type: "CosineSimRetrieval"
        params:
          tables_limit: 5
          columns_limit: 10

      context_processing:
        type: "SimpleContextProcessor"
        params:
          include_table_descriptions: true

      prompt_building:
        type: "StandardPromptBuilder"
        params:
          template_file: "path/to/custom_template.txt"

      llm_interaction:
        type: "DirectLLMInteraction"
        params:
          temperature: 0.1

      response_processing:
        type: "SQLResponseProcessor"
        params:
          max_preview_rows: 20
      ```

7. Run the application:

```
python main.py
```

**The app will be available at http://localhost:5000**

## 🤝 Contributing

Feel free to dive in! Here's how:

1. Fork it
2. Create your feature branch (git checkout -b feature/awesome-feature)
3. Commit your changes (git commit -m 'Add awesome feature')
4. Push to the branch (git push origin feature/awesome-feature)
5. Create a Pull Request

## 📝 License

**_Copyright 2024_**

Licensed under the Apache License, Version 2.0 (the "License");  
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at

```
http://www.apache.org/licenses/LICENSE-2.0
```

Unless required by applicable law or agreed to in writing, software  
distributed under the License is distributed on an "AS IS" BASIS,  
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and  
limitations under the License.

## 📧 Contact

Got questions? Reach out to pracucci.giacomo@gmail.com
