from pymongo.mongo_client import MongoClient
from typing import List, Dict, Tuple

client = None  # Global variable to store the MongoDB client
db = None      # Global variable to store the MongoDB database

def initialize(MONGO_URL: str, DB_name: str):
    """
    Initializes the MongoDB client and establishes a connection to the database.
    """
    global client, db
    try:
        client = MongoClient(MONGO_URL)  # Create the MongoDB client
        client.admin.command('ping')    # Check server availability
        db = client[DB_name]           # Select the database
    except Exception as e:
        print(f"Error: {str(e)} while initializing MongoDB.")

def load_all_to_dictionary(where_to_load: Dict[str, Tuple], collection_name: str):
    """
    Loads all data from the collection into a dictionary where keys map to tuples of values.
    """
    try:
        for data_line in db[collection_name].find():  # Fetch data from the collection
            key = data_line.get("key")               # Retrieve the key
            values = data_line.get("values")         # Retrieve the values
            if key is not None and values is not None:
                where_to_load[key] = tuple(values)   # Add to the dictionary
    except Exception as e:
        print(f"Error: {str(e)} while loading all to the dictionary.")

def load_all_to_array(where_to_load: List, collection_name: str):
    """
    Loads all data from the collection into a list.
    """
    try:
        for data_line in db[collection_name].find():  # Fetch data from the collection
            value = data_line.get("value")           # Retrieve the value
            if value is not None:
                where_to_load.append(value)          # Add to the list
    except Exception as e:
        print(f"Error: {str(e)} while loading all to the array.")

def insert_one_dictionary_item(key: str, values: Tuple, collection_name: str):
    """
    Inserts a single item into the dictionary with a key and a tuple of values.
    """
    try:
        data = {"key": key, "values": list(values)}  # Prepare the document
        db[collection_name].insert_one(data)        # Insert into the collection
    except Exception as e:
        print(f"Error: {str(e)} while inserting one dictionary item.")

def insert_one_array_item(value, collection_name: str):
    """
    Inserts a single item into the array with a value.
    """
    try:
        db[collection_name].insert_one({"value": value})  # Insert into the collection
    except Exception as e:
        print(f"Error: {str(e)} while inserting one array item.")

def delete_one_dictionary_item(key: str, collection_name: str):
    """
    Deletes a single item from the dictionary by key.
    """
    try:
        db[collection_name].delete_one({"key": key})  # Delete from the collection
    except Exception as e:
        print(f"Error: {str(e)} while deleting one dictionary item.")

def delete_one_array_item(value, collection_name: str):
    """
    Deletes a single item from the array by value.
    """
    try:
        db[collection_name].delete_one({"value": value})  # Delete from the collection
    except Exception as e:
        print(f"Error: {str(e)} while deleting one array item.")

def close_connection():
    """
    Closes the MongoDB connection.
    """
    global client
    if client:
        client.close()  # Close the connection
        print("MongoDB connection closed.")







