import sqlite3

# Define the path to the SQLite database
DB_NAME = "src/database/legal_rag.db"

# Create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Create the application_logs table
def create_application_logs():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS application_logs
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     session_id TEXT,
                     user_id INTEGER,
                     user_query TEXT,
                     rag_response TEXT,
                     model TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     FOREIGN KEY(user_id) REFERENCES users(id))''')
    conn.close()

# Insert a new row into the application_logs table
def insert_application_logs(session_id, user_id, user_query, rag_response, model):
    conn = get_db_connection()
    conn.execute('INSERT INTO application_logs (session_id, user_id, user_query, rag_response, model) VALUES (?, ?, ?, ?, ?)',
                 (session_id, user_id, user_query, rag_response, model))
    conn.commit()
    conn.close()

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

# Insert a new row into the users table
def insert_user(username, email, password):
    conn = get_db_connection()
    conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
    conn.commit()
    conn.close()

# Get a user from the users table
def get_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Get chat history for a given session ID
def get_chat_history(session_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_query, rag_response FROM application_logs WHERE session_id = ? AND user_id = ? ORDER BY created_at', (session_id, user_id))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            {"role": "human", "content": row['user_query']},
            {"role": "ai", "content": row['rag_response']}
        ])
    conn.close()
    return messages

# Get all chat sessions for a given user
def get_all_chats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT session_id FROM application_logs WHERE user_id = ? ORDER BY created_at', (user_id,))
    sessions = cursor.fetchall()
    conn.close()
    return [session['session_id'] for session in sessions]

# Initialize the database tables
create_application_logs()
create_users_table()