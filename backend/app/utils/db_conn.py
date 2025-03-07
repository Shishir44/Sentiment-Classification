from pymongo import MongoClient
import os
import json
import asyncio
from datetime import datetime
repo_path = os.path.join(os.getcwd())
cur_dir = os.getcwd()

def load_config_json(path:str=None):

    if path is None:
        path = "config.json" 

    os.chdir(cur_dir)
    with open(path, "r") as f:
        data = json.load(f)

    return data

mongo_uri = load_config_json()["MONGO_URI"]
client = MongoClient(mongo_uri)
db = client["Sentiment_Classification"]

RESPONSE = db["response"]
COMMENTS = db["comments"]
POSTS = db["posts"]
USERS = db["users"]

def load_config(var_key=None):
    """ Load configuration from config.json file. """
    path = os.path.join(repo_path, "config.json")
    with open(path, "r") as f:
        data = json.load(f)
    if var_key:
        return data.get(var_key)
    return data



def user_profile(client, req, result):
    collection = client["users"]
    existing_user = collection.find_one({"user_id": req.user_id})

    # Create the new response dictionary
    new_response = {
        "response": req.comment_text,  # Assuming this is the message from the user
        "sentiment": result.get("sentiment", None),
        "timestamp": datetime.now(),
    }

    if existing_user:
        # Update the existing user by adding a new response
        collection.update_one(
            {"user_id": req.user_id},
            {
                "$push": {
                    "responses": new_response  # Append the new response to the responses array
                }
            }
        )
    else:
        # Insert a new user with the initial response
        collection.insert_one(
            {
                "user_id": req.user_id,
                "user_name": req.user_name,
                "responses": [new_response],  # Start with the first response in a list
                "created_at": datetime.now(),
            }
        )

def response(client, req, result):
    collection = client["response"]
    resp = collection.insert_one(
        {   
            "user_name": req.user_name,
            "comment_id": req.comment_id,
            "request": req.dict(),
            "response": result,
            "timestamp": datetime.now(),
        }
    )

def posts(client, req):
    collection = client["posts"]
    existing_post = collection.find_one({"post_id": req.post_id})
    
    post_details = {
        "post_title": req.post_title,
        "post_caption": req.post_caption,
        "created_at": req.post_date,
    }

    if existing_post:
        # Update the existing post
        collection.update_one(
            {"post_id": req.post_id},
            {
                "$set": post_details  # Corrected this line
            }
        )
    else:
        # Insert a new post
        collection.insert_one(
            {
                "post_id": req.post_id,
                **post_details  # Use unpacking to include post_details
            }
        )

def comments(client, req, result):
    collection = client["comments"]
    existing_comment = collection.find_one({"comment_id": req.comment_id})

    comment_details = {
        "user_name": req.user_name,
        "user_id": req.user_id,
        "comment": req.comment_text,
        "post_id": req.post_id,
        "commented_date":req.comment_date,
        "sentiment": result.get("sentiment", None),
    }

    if existing_comment:
        # Update the existing comment
        collection.update_one(
            {"comment_id": req.comment_id},
            {
                "$set": comment_details  # Update the existing fields
            }
        )
    else:
        # Insert a new comment
        collection.insert_one(
            {
                "comment_id": req.comment_id,
                **comment_details  # Use unpacking to include comment_details
            }
        )


async def insert_into_db(req, result):
    client = MongoClient(load_config("MONGO_URI"))["Sentiment_Classification"]
    user_profile(client, req, result)
    response(client, req, result)
    posts(client, req)
    comments(client, req, result)

if __name__ == "__main__":
    a = load_config("MONGO_URI")
    print(a)
