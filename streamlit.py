import streamlit as st
from github import Github
import json
import hashlib

# GitHub access token — you will need to create a personal access token and add here

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_file(username):
    try:
        file = repo.get_contents(f"users/{username}.json")
        return file
    except:
        return None

def read_user(username):
    file = get_user_file(username)
    if not file:
        return None
    content = file.decoded_content.decode()
    return json.loads(content)

def save_user(username, password):
    content = json.dumps({
        "username": username,
        "password": hash_password(password)
    }, indent=2)
    try:
        file = get_user_file(username)
        # If exists, update
        repo.update_file(file.path, f"Update {username}", content, file.sha)
    except:
        # If not exists, create new file
        repo.create_file(f"users/{username}.json", f"Create {username}", content)

def login(username, password):
    user = read_user(username)
    if not user:
        return {"success": False, "error": "User not found"}
    if user["password"] == hash_password(password):
        return {"success": True, "message": "Login successful"}
    return {"success": False, "error": "Incorrect password"}

def signup(username, password):
    user = read_user(username)
    if user:
        return {"success": False, "error": "User already exists"}
    save_user(username, password)
    return {"success": True, "message": "Signup successful"}

# Streamlit app

st.title("Login / Signup API")

flag = st.selectbox("Select operation", ["Login (1)", "Signup (2)"])
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Submit"):
    if not username or not password:
        st.error("Please enter username and password")
    else:
        if flag.startswith("Login"):
            res = login(username, password)
        else:
            res = signup(username, password)
        st.json(res)
