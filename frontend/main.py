import streamlit as st
import os

pages_config = {
  "Dashboard": "dashboard.py",
  "Comments": "comments.py",
  "Users": "users.py",
  "Posts": "posts.py",
}

def menu():
    st.sidebar.image(os.path.join("assets", "nextai-logo.png"), width=200)
