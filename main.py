""" TEST CONNETTORE
from connettori.db_manager import DatabaseManager

db = DatabaseManager(
    host="localhost",
    port="5432",
    database="postgres",
    user="postgres",
    password="admin"
)

if db.connect():
    query = "SELECT * FROM video_games.game LIMIT 5;"
    df = db.execute_query(query)
    
    if df is not None:
        print(df.head())
    
    db.close()
"""

""" TEST OPENAI
from openAI.openai_handler import OpenAIManager

openai_manager = OpenAIManager(
    api_key="your-api-key-here",
    embedding_model="text-embedding-3-large",
    chat_model="gpt-4o"
)

text = "Questo è un esempio di testo"
embedding = openai_manager.get_embedding(text)

prompt = "Qual è la capitale dell'Italia?"
response = openai_manager.get_completion(prompt)


texts = ["testo 1", "testo 2", "testo 3"]
embeddings = openai_manager.get_embeddings_batch(texts)

for chunk in openai_manager.get_chat_stream("Raccontami una storia"):
    print(chunk, end='', flush=True)
    
"""