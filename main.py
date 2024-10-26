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