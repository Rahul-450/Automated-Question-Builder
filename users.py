# users.py

import json
import getpass

USERS_FILE = 'data/users.json'

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}
    return users

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def authenticate():
    users = load_users()
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    user = users.get(username)
    if user and user['password'] == password:
        print(f"Welcome, {username}!")
        user['username'] = username  # Add this line
        return user
    else:
        print("Invalid username or password.")
        return None

def add_user(username, password, role):
    users = load_users()
    if username in users:
        print("User already exists.")
        return False
    users[username] = {'password': password, 'role': role}
    save_users(users)
    print(f"User {username} added successfully.")
    return True

def remove_user(username):
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        print(f"User {username} removed successfully.")
        return True
    else:
        print("User does not exist.")
        return False

def update_user(username, password=None, role=None):
    users = load_users()
    if username in users:
        if password:
            users[username]['password'] = password
        if role:
            users[username]['role'] = role
        save_users(users)
        print(f"User {username} updated successfully.")
        return True
    else:
        print("User does not exist.")
        return False