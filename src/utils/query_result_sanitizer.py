import datetime
from typing import Any, Dict, List, Union


def sanitize_for_json(data: Any) -> Any:
    """
    Recursively sanitize data to ensure it's JSON serializable.
    Handles memoryview objects, datetime objects, and other non-serializable types.
    
    Args:
        data: Any Python object to sanitize
        
    Returns:
        JSON serializable version of the data
    """
    # Handle None
    if data is None:
        return None
        
    # Handle lists - recursively sanitize each item
    if isinstance(data, list):
        return [sanitize_for_json(item) for item in data]
        
    # Handle dictionaries - recursively sanitize each value
    if isinstance(data, dict):
        return {key: sanitize_for_json(value) for key, value in data.items()}
        
    # Handle memoryview objects (binary data)
    if isinstance(data, memoryview):
        return "[binary data]"  # Replace with placeholder
        
    # Handle bytes
    if isinstance(data, bytes):
        return "[binary data]"  # Replace with placeholder
        
    # Handle datetime objects
    if isinstance(data, (datetime.date, datetime.datetime)):
        return data.isoformat()
        
    # Return primitives that are already serializable
    return data


def sanitize_query_results(results: Union[List[Dict], Dict]) -> Union[List[Dict], Dict]:
    """
    Sanitize SQL query results to ensure they're JSON serializable.
    
    Args:
        results: Query results from database
        
    Returns:
        Sanitized version of the query results
    """
    return sanitize_for_json(results)
