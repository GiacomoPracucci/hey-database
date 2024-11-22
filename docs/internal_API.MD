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