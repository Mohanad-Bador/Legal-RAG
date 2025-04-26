import sqlite3
import json

# Define the path to the SQLite database
DB_NAME = "src/database/legal_rag.db"

# Create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Create the messages table - modified to include rag_answer column
def create_messages_table():
    conn = get_db_connection()
    # First check if the table exists and drop it to recreate with the new schema
    conn.execute('DROP TABLE IF EXISTS messages')
    conn.execute('''CREATE TABLE IF NOT EXISTS messages
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     chat_id INTEGER,
                     user_query TEXT,
                     rag_answer TEXT,
                     rag_response TEXT,
                     model TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     FOREIGN KEY(chat_id) REFERENCES chats(id))''')
    conn.close()

# Create the chats table
def create_chats_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS chats
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER,
                     title TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.close()

# Insert a new message into the messages table - fixed VALUES clause to match parameter count
def insert_message(chat_id, user_query, rag_answer, rag_response, model):
    conn = get_db_connection()
    conn.execute('INSERT INTO messages (chat_id, user_query, rag_answer, rag_response, model) VALUES (?, ?, ?, ?, ?)',
                 (chat_id, user_query, rag_answer, rag_response, model))
    conn.commit()
    conn.close()

# Create a new chat for a user
def create_chat(user_id, title="New Chat"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO chats (user_id, title) VALUES (?, ?)', (user_id, title))
    conn.commit()
    chat_id = cursor.lastrowid
    conn.close()
    return chat_id

# Create the users table
def create_users_table():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE,
                     email TEXT UNIQUE,
                     password TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()

# Insert a new user into the users table
def insert_user(username, email, hashed_password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
        (username, email, hashed_password)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

# Get a user from the users table
def get_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Get all chats for a given user
def get_user_chats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, created_at FROM chats WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    chats = cursor.fetchall()
    conn.close()
    return chats

# Get chat history for a given chat ID
def get_chat_history(chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_query, rag_answer FROM messages WHERE chat_id = ? ORDER BY created_at', (chat_id,))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            {"role": "human", "content": row['user_query']},
            {"role": "ai", "content": row['rag_answer']}
        ])
    conn.close()
    return messages

# Get a chat by its ID
def get_chat_by_id(chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM chats WHERE id = ?', (chat_id,))
    chat = cursor.fetchone()
    conn.close()
    return chat

# Update chat title
def update_chat_title(chat_id, new_title):
    conn = get_db_connection()
    conn.execute('UPDATE chats SET title = ? WHERE id = ?', (new_title, chat_id))
    conn.commit()
    conn.close()

# Delete a chat and its messages
def delete_chat(chat_id):
    conn = get_db_connection()
    # First delete all messages associated with the chat
    conn.execute('DELETE FROM messages WHERE chat_id = ?', (chat_id,))
    # Then delete the chat itself
    conn.execute('DELETE FROM chats WHERE id = ?', (chat_id,))
    conn.commit()
    conn.close()

# Initialize the database tables
def initialize_database():
    create_users_table()
    create_chats_table()
    create_messages_table()

# Initialize the database on import
initialize_database()