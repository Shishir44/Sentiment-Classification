import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import json


# Load MongoDB configuration from config.json
with open("config.json") as config_file:
    config = json.load(config_file)


# MongoDB connection setup
client = MongoClient(config["MONGO_URI"])  # Update with your MongoDB URI
db = client[config["Sentiment_Classification"]] # Replace with your database name
posts_collection = db[config["posts"]]  # Replace with your collection name

# Helper function to fetch all posts
def fetch_posts():
    return list(posts_collection.find({}, {"title": 1, "description": 1, "created_at": 1}))

# Helper function to fetch a post by ID
def fetch_post_by_id(post_id):
    return posts_collection.find_one({"_id": post_id})

# Streamlit UI
st.title("Comments Page")

# Step 1: Select a Post
st.subheader("Select a Post")
posts = fetch_posts()

# Create a selection dropdown for available posts
post_options = {post["_id"]: post["title"] for post in posts}
selected_post_id = st.selectbox("Choose a post", options=post_options.keys(), format_func=lambda x: post_options[x])

# Step 2: Display Selected Post Information
if selected_post_id:
    post = fetch_post_by_id(selected_post_id)
    if post:
        st.header(post["title"])
        st.write("**Description:**", post["description"])
        st.write("**Post ID:**", post["_id"])
        st.write("**Created At:**", post["created_at"].strftime("%Y-%m-%d %H:%M:%S"))

        st.markdown("---")  # Separator line

        # Step 3: Display Comments
        st.subheader("Comments")
        for i, comment in enumerate(post.get("comments", []), 1):
            with st.expander(f"Comment {i}: {comment['text']}"):
                st.write("**Comment ID:**", comment["id"])
                st.write("**Commented by:**", comment["commented_by"])
                st.write("**Sentiment:**", comment["sentiment"])
    else:
        st.write("Selected post not found.")
