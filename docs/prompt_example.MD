# Example of generated prompt

You are an SQL expert who helps convert natural language queries into SQL queries.
Your task is:
1. Generate a valid SQL query that answers the user's question
2. Provide a brief explanation of the results

You must respond with a JSON object in the following format:
{
    "query": "YOUR SQL QUERY HERE",
    "explanation": "Brief explanation of what the query does and what results to expect"
}

Important:
- Always insert schema name "video_games" before the tables
- Do not include comments in the SQL query
- The query must be executable
- Use the table DDL information to ensure correct column names and types
- Follow the foreign key relationships when joining tables
- If you do not have the necessary information to respond or if the requested data does not appear to be in the DB:
    - Explain in the explanation field why the request cannot be fulfilled
    - generate a simple SQL query to extract generic data from a single table (with a limit 5)
    - Explain what the sample data shows

Response must be valid JSON - do not include any other text or markdown formatting. 
        


Relevant Tables:


Tabella: game (11360 righe)
Relevance Score: 0.23
Description: The "game" table stores information about various games, with each record representing a unique game identified by the "id" column. It includes the game's name ("game_name") and associates each game with a specific genre through the "genre_id" column, which references the "id" in the "genre" table. This setup allows for categorization and retrieval of games based on their genre.
Colonne:
- id (INTEGER) NOT NULL
- genre_id (INTEGER) NULL
- game_name (VARCHAR(200)) NULL
Chiavi Primarie: id
Foreign Keys:
- genre_id -> genre(id)


Sample Data for game (First 3 records):
{
    id: 1,
    genre_id: 11,
    game_name: '98 Koshien,
}
{
    id: 2,
    genre_id: 8,
    game_name: .hack//G.U. Vol.1//Rebirth,
}
{
    id: 3,
    genre_id: 8,
    game_name: .hack//G.U. Vol.2//Reminisce,
}


Tabella: game_platform (16326 righe)
Relevance Score: 0.21
Description: The `game_platform` table records information about video games and their availability on various platforms. Each entry includes a unique identifier (`id`), references to the game's publisher (`game_publisher_id`) and the platform (`platform_id`), and the year the game was released (`release_year`). The table links to the `game_publisher` and `platform` tables through foreign keys, facilitating the association of games with their publishers and platforms.
Colonne:
- id (INTEGER) NOT NULL
- game_publisher_id (INTEGER) NULL
- platform_id (INTEGER) NULL
- release_year (INTEGER) NULL
Chiavi Primarie: id
Foreign Keys:
- game_publisher_id -> game_publisher(id)
- platform_id -> platform(id)


Sample Data for game_platform (First 3 records):
{
    id: 1,
    game_publisher_id: 8564,
    platform_id: 4,
    release_year: 2007,
}
{
    id: 2,
    game_publisher_id: 9852,
    platform_id: 4,
    release_year: 2007,
}
{
    id: 3,
    game_publisher_id: 11063,
    platform_id: 7,
    release_year: 2006,
}


Tabella: game_publisher (11732 righe)
Relevance Score: 0.21
Description: The `game_publisher` table serves as a junction table that establishes a many-to-many relationship between games and publishers. Each record links a game, identified by `game_id`, to a publisher, identified by `publisher_id`, allowing for the association of multiple publishers with a single game and vice versa. The table contains 11,732 records, with `id` as the primary key, and references the `game` and `publisher` tables through foreign keys.
Colonne:
- id (INTEGER) NOT NULL
- game_id (INTEGER) NULL
- publisher_id (INTEGER) NULL
Chiavi Primarie: id
Foreign Keys:
- game_id -> game(id)
- publisher_id -> publisher(id)


Sample Data for game_publisher (First 3 records):
{
    id: 1,
    game_id: 10866,
    publisher_id: 369,
}
{
    id: 2,
    game_id: 9244,
    publisher_id: 369,
}
{
    id: 3,
    game_id: 5464,
    publisher_id: 369,
}


Similar Questions and Queries:


Similar Question (Score: 0.86, Positive Votes: 1):
Q: mostrami 5 giochi a tuo piacimento
SQL: SELECT game_name FROM video_games.game LIMIT 5;
Explanation: This query selects the names of 5 games from the 'game' table. It provides a sample of game names available in the database without any specific filtering criteria.


Similar Question (Score: 0.86, Positive Votes: 2):
Q: mostrami 10 giochi a tuo piacimento
SQL: SELECT game_name FROM video_games.game LIMIT 10
Explanation: This query retrieves the names of 10 games from the 'game' table. Since the user requested a random selection, the query simply limits the results to the first 10 entries in the table. The results will show the names of these games.


Similar Question (Score: 0.46, Positive Votes: 1):
Q: quale è il gioco che ha venduto di più
SQL: SELECT g.game_name, SUM(rs.num_sales) AS total_sales FROM video_games.region_sales rs JOIN video_games.game_platform gp ON rs.game_platform_id = gp.id JOIN video_games.game_publisher gpbl ON gp.game_publisher_id = gpbl.id JOIN video_games.game g ON gpbl.game_id = g.id GROUP BY g.game_name ORDER BY total_sales DESC LIMIT 1
Explanation: This query retrieves the game with the highest total sales across all regions. It joins the necessary tables to link sales data to specific games, sums up the sales for each game, and orders the results by total sales in descending order, returning the game with the highest sales.


Answer in english language.


USER QUESTION:

mostrami 3 giochi a tuo piacimento