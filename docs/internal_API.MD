# Internal API Documentation

## Overview

This document describes the internal API endpoints used by the web application to handle chat interactions and database schema visualization.

## Base URLs
- Chat endpoints: /chat
- Schema endpoints: /schema

## Chat API Endpoints

### Send Chat Message

Process a user message and get a SQL query response.
**Endpoint**: POST /chat/api/chat
**Request Body**:  
```json 
{
    "message": string    // The user's message/question
}
```
**Response**:
```json 
{
    "success": boolean,
    "query": string,              // The generated SQL query
    "explanation": string,        // Natural language explanation of the query
    "results": array,            // Query execution results
    "preview": array,            // Optional preview data
    "original_question": string,  // The original user question
    "from_vector_store": boolean, // Whether response was cached
    "error": string              // Present only if success is false
}
```
**Example Success Response:**
```json 
{
    "success": true,
    "query": "SELECT * FROM games LIMIT 5",
    "explanation": "This query retrieves the first 5 games from the database",
    "results": [
        {
            "id": 1,
            "name": "Game Name",
            // ... other columns
        }
    ],
    "original_question": "Show me some games",
    "from_vector_store": false
}
```
**Example Error Response:**
```json 
{
    "success": false,
    "error": "Failed to execute query: syntax error"
}
```

### Submit Feedback

Submit positive feedback for a successful query interaction.
**Endpoint**: POST /chat/api/feedback
**Request Body**:
```json 
{
    "question": string,     // Original user question
    "sql_query": string,    // The SQL query that was generated
    "explanation": string   // The explanation provided
}
```
**Response**:
```json 
{
    "success": boolean,
    "error": string        // Present only if success is false
}
```
**Possible Error Responses**:
- Vector store disabled: 
    ```json 
    {
        "success": false,
        "error": "vector_store_disabled",
        "message": "Il Vector Store non è abilitato. Abilitalo per utilizzare questa funzionalità."
    }
    ```

## Schema API Endpoints

### Get Database Schema
Retrieve the complete database schema metadata.
**Endpoint**: GET /schema/api/metadata
**Response**:
```json 
{
    "success": boolean,
    "data": {
        "tables": [
            {
                "name": string,
                "columns": [
                    {
                        "name": string,
                        "type": string,
                        "nullable": boolean,
                        "isPrimaryKey": boolean
                    }
                ],
                "relationships": [
                    {
                        "fromColumns": string[],
                        "toTable": string,
                        "toColumns": string[]
                    }
                ]
            }
        ]
    }
}
```
**Example Success Response**:
```json 
{
    "success": true,
    "data": {
        "tables": [
            {
                "name": "games",
                "columns": [
                    {
                        "name": "id",
                        "type": "INTEGER",
                        "nullable": false,
                        "isPrimaryKey": true
                    },
                    {
                        "name": "title",
                        "type": "VARCHAR",
                        "nullable": false,
                        "isPrimaryKey": false
                    }
                ],
                "relationships": [
                    {
                        "fromColumns": ["genre_id"],
                        "toTable": "genres",
                        "toColumns": ["id"]
                    }
                ]
            }
        ]
    }
}
```

## Error Handling
All API endpoints follow a consistent error response format:
```json 
{
    "success": false,
    "error": string  // Error description
}
```
Common HTTP Status Codes:
- 200: Success
- 400: Bad Request (missing or invalid parameters)
- 500: Internal Server Error

## Notes

- All endpoints return JSON responses
- Errors are always returned with `success: false` and an error message
- The vector store functionality must be enabled in the configuration for the feedback endpoint to work
- The chat service maintains a connection to the database throughout its lifecycle
- Schema metadata is cached at the application level for improved performance

## Configuration Dependencies
The API functionality depends on the following configuration settings in config.yaml:
- Database connection parameters
- LLM settings (OpenAI or Ollama)
- Vector store configuration (if enabled)
- Debug mode settings