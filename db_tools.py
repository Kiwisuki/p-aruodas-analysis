from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import logging
from typing import Dict, Set

URI = "mongodb+srv://Kiwisaki:testas123@scraping.hcncqvy.mongodb.net/?retryWrites=true&w=majority"

def save_property(property: Dict, ad_type: str) -> None:
    # Upload to MongoDB
    client = MongoClient(URI, server_api=ServerApi('1'))
    db = client['Scraping']
    collection = db[f'aruodas/{ad_type}']

    # insert and use Ad_id as the primary key
    collection.insert_one(property)
    logging.info(f'Inserted property {property["_id"]} into {collection.name}')


def get_scraped_properties(ad_type: str) -> Set:
    # Get all _ids from MongoDB
    client = MongoClient(URI, server_api=ServerApi('1'))
    db = client['Scraping']
    collection = db[f'aruodas/{ad_type}']
    
    return set([property['_id'] for property in collection.find({}, {'_id': 1})])