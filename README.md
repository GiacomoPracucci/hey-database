# Hey, Database! SQL Chatbot

A Flask-based web application that lets users query a video games database using natural language.  
The app translates user questions into SQL queries using LLMs (supports both OpenAI and Ollama models) and returns formatted results.

![heydatabase1](https://github.com/user-attachments/assets/edd0992a-a5b5-4498-b8b4-1748d030869b)



## 🚀 Features

- Natural language to SQL translation  
- Support for both OpenAI and Ollama LLMs  
- Real-time query execution  
- Interactive chat interface  
- Query explanation for better understanding  
- Error handling with detailed feedback
- Multiple database support (PostgreSQL, MySQL, Snowflake)
- Query caching with vector store:
   - Store and retrieve similar queries
   - Supports multiple embedding models (OpenAI, HuggingFace)
- User feedback system:
   - Thumbs up for correct queries
   - Automatic storage of validated queries

## 🛠️ Tech Stack

- Backend: Python, Flask
- Frontend: HTML, CSS, JavaScript
- Databases:   
   - PostgreSQL  
   - MySQL  
   - Snowflake  
- LLM Integration:  
   - OpenAI API  
   - Ollama (local models)  
- Vector Store:
   - Qdrant for query storage
- Embedding Models:
   - HuggingFace Sentence Transformers
   - OpenAI Embeddings
- Database Access: SQLAlchemy  

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
      type: postgres  # or mysql or snowflake
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
         type: huggingface    # or openai
         model_name: sentence-transformers/multi-qa-MiniLM-L6-cos-v1
         # api_key: ${OPENAI_API_KEY}  # required for OpenAI embeddings
   ```

6. Initialize the database:

   Sample video_games schema at https://github.com/bbrumm/databasestar/tree/main/sample_databases/sample_db_videogames  

For PostgreSQL:  
   - Create a database
   - Import your video games data into the "video_games" schema  
  
For MySQL:  
   - Create a database  
   - Import your video games data  
   - Ensure you're using the Strong Password Authentication method  
  
For Snowflake:  
   - Have a working Snowflake account  
   - Set up your warehouse, database, and schema  
   - Import your video games data  

7. Run the application:
```
python main.py
```

   **The app will be available at http://localhost:5000**

## 💡 Usage

1. Open your browser and navigate to http://localhost:5000  
2. Type your question about video games data in natural language  
3. The app will:  
- Convert your question to SQL
- Execute the query  
- Show you the SQL query used  
- Display the results in a formatted table  
- Provide an explanation of what the query does  


## 🔍 Project Structure:
```
hey-database/
│   .gitignore
│   config.yaml
│   LICENSE
│   main.py
│   README.md
│   requirements.txt
|   .env # you have to create and populate it
│
├───data
│   └─── your vectorstores
│
├───docs
│       add_components.MD
│       configuration.MD
│       query_caching_doc_0911.MD
│
└───src
    ├───config
    │   │   config_loader.py
    │   │   factory.py
    │   │   models.py
    │
    ├───connettori
    │   │   base_connector.py
    │   │   mysql.py
    │   │   postgres.py
    │   │   snowflake.py
    │
    ├───dbcontext
    │   │   base_metadata_retriever.py
    │   │   mysql_metadata_retriever.py
    │   │   postgres_metadata_retriever.py
    │   │   snowflake_metadata_retriever.py
    │
    ├───embedding
    │   │   base_embedding_model.py
    │   │   huggingface_embedding.py
    │   │   openai_embedding.py
    │
    ├───llm_input
    │   │   prompt_generator.py
    ├───llm_output
    │   │   response_handler.py
    ├───ollama_
    │   │   ollama_handler.py
    │
    ├───openai_
    │   │   openai_handler.py
    ├───store
    │   │   base_vectorstore.py
    │   │   qdrant_vectorstore.py
    └───web
        │   chat_service.py
        │   routes.py
        │
        ├───static
        │       script.js
        │       style.css
        │
        ├───templates
        │       base.html
        │       index.html
```

## 🤝 Contributing
Feel free to dive in! Here's how:

1. Fork it  
2. Create your feature branch (git checkout -b feature/awesome-feature)  
3. Commit your changes (git commit -m 'Add awesome feature')  
4. Push to the branch (git push origin feature/awesome-feature)  
5. Create a Pull Request

## 📝 License
***Copyright 2024***

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
