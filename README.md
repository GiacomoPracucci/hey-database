# Hey, Database! SQL Chatbot

A Flask-based web application that lets users query a video games database using natural language.  
The app translates user questions into SQL queries using LLMs (supports both OpenAI and Ollama models) and returns formatted results.

## 🚀 Features

- Natural language to SQL translation  
- Support for both OpenAI and Ollama LLMs  
- Real-time query execution  
- Interactive chat interface  
- Query explanation for better understanding  
- Copy-to-clipboard functionality for SQL queries  
- Error handling with detailed feedback

## 🛠️ Tech Stack

- Backend: Python, Flask
- Frontend: HTML, CSS, JavaScript
- Database: PostgreSQL
- LLM Integration: OpenAI API / Ollama
- ORM: SQLAlchemy
- Data Processing: Pandas

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database
- OpenAI API key (if using OpenAI) or Ollama instance (if using local models)

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


5. Initialize the database:  
   
- Make sure PostgreSQL is running  
- Create a database called "postgres" (or update the config to use a different name)  
- Import your video games data into the "video_games" schema

6. Run the application:
```
python main.py
```

The app will be available at http://localhost:5000

## 💡 Usage

1. Open your browser and navigate to http://localhost:5000  
2. Type your question about video games data in natural language  
3. The app will:  
- Convert your question to SQL
- Execute the query  
- Show you the SQL query used  
- Display the results in a formatted table  
- Provide an explanation of what the query does  

Example questions:

- "Show me the first 5 games in the database"  
- "What are the most popular genres?"

## 🔍 Project Structure:
```
sql-chatbot/
├── main.py                 # Application entry point
├── src/
│   ├── web/               # Web-related components
│   │   ├── routes.py      # Flask routes
│   │   ├── templates/     # HTML templates
│   │   └── static/        # CSS, JS files
│   ├── dbcontext/         # Database handling
│   ├── prompt/            # LLM prompt management
│   └── connettori/        # Database connectors
├── requirements.txt        # Python dependencies
└── .env                   # Environment variables
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
