from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import os
from typing import Optional

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["csv_rag_db"]
files_collection = db["files"]

def get_db():
    """Database dependency for FastAPI"""
    try:
        client.admin.command('ping')
        return db
    except ConnectionFailure:
        raise ConnectionError("MongoDB connection failed")

def store_csv(file_id: str, file_name: str, document: dict, metadata: Optional[dict] = None):
    try:
        files_collection.insert_one({
            "file_id": file_id,
            "file_name": file_name,
            "document": document,
            "metadata": metadata or {}
        })
    except PyMongoError as e:
        raise Exception(f"Database operation failed: {str(e)}")