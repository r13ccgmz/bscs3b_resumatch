import sqlite3
import os

def connect_db():
    # Get the absolute path of the directory where models.py is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Define the database file path within this directory
    db_path = os.path.join(script_dir, 'interviewees.db')
    return sqlite3.connect(db_path)

def init_db():
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS interviewees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_interviewee(applicant_info):
    conn = connect_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO interviewees (name, email) VALUES (?, ?)
    ''', (applicant_info['name'], applicant_info['email']))
    conn.commit()
    conn.close()

# Initialize the database when the module is run directly
if __name__ == '__main__':
    init_db()