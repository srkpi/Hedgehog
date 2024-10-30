from pymongo.mongo_client import MongoClient
from typing import List, Dict, Tuple

client = None
db = None

def initialize(MONGO_URL: str, DB_name: str):
    """Initialize the MongoDB client and database."""
    global client, db
    try:
        client = MongoClient(MONGO_URL)
        client.admin.command('ping')
        db = client[DB_name]
    except Exception as e:
        print(f"Error: {str(e)} while initializing MongoDB.")

def load_all_to_dictionary(where_to_load: Dict[str, Tuple], collection_name: str):
    """Load all data into a dictionary where keys map to tuples of values."""
    try:
        for data_line in db[collection_name].find():
            key = data_line.get("key")
            values = data_line.get("values")
            if key is not None and values is not None:
                where_to_load[key] = tuple(values)
    except Exception as e:
        print(f"Error: {str(e)} while loading all to the dictionary.")

def load_all_to_array(where_to_load: List, collection_name: str):
    """Load all data into a list."""
    try:
        for data_line in db[collection_name].find():
            value = data_line.get("value")
            if value is not None:
                where_to_load.append(value)
    except Exception as e:
        print(f"Error: {str(e)} while loading all to the array.")

def insert_one_dictionary_item(key: str, values: Tuple, collection_name: str):
    """Insert a single item with a key and a tuple of values."""
    try:
        data = {"key": key, "values": list(values)}
        db[collection_name].insert_one(data)
    except Exception as e:
        print(f"Error: {str(e)} while inserting one dictionary item.")

def insert_one_array_item(value, collection_name: str):
    """Insert a single item with a value."""
    try:
        db[collection_name].insert_one({"value": value})
    except Exception as e:
        print(f"Error: {str(e)} while inserting one array item.")

def delete_one_dictionary_item(key: str, collection_name: str):
    """Delete a single item by key."""
    try:
        db[collection_name].delete_one({"key": key})
    except Exception as e:
        print(f"Error: {str(e)} while deleting one dictionary item.")

def delete_one_array_item(value, collection_name: str):
    """Delete a single item by value."""
    try:
        db[collection_name].delete_one({"value": value})
    except Exception as e:
        print(f"Error: {str(e)} while deleting one array item.")

def close_connection():
    """Close the MongoDB connection."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed.")







