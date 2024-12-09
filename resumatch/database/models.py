import sqlite3

DATABASE = 'interviewees.db'
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interviewees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            qualification_grade REAL NOT NULL,
            skills_score REAL NOT NULL,
            education_score REAL NOT NULL,
            experience_score REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    ''')
    conn.commit()
    conn.close()

def add_interviewee(applicant_info, qualification_grade, skills_score, education_score, experience_score, status):
    # Connect to the SQLite3 database (or create it if it doesn't exist)
    conn = sqlite3.connect('interviewees.db')  # Replace 'database.db' with your actual database file
    cursor = conn.cursor()

    # SQL query to insert a new interviewee
    query = '''
    INSERT INTO interviewees (name, email, qualification_grade, skills_score, education_score, experience_score, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    '''
    # Extract the applicant's information
    applicant_name = applicant_info.get('name', 'Applicant')
    applicant_email = applicant_info.get('email', '')
    
    # Insert the new interviewee data into the database
    cursor.execute(query, (
        applicant_name,
        applicant_email,
        qualification_grade,
        skills_score,
        education_score,
        experience_score,
        status
    ))

    conn.commit()
    conn.close()

def get_all_interviewees():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM interviewees')
    interviewees = cursor.fetchall()
    conn.close()
    return interviewees

def get_interviewee_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM interviewees WHERE id = ?', (id,))
    interviewee = cursor.fetchone()
    conn.close()
    return interviewee

def update_interviewee(id, updated_info):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE interviewees
        SET name = ?, email = ?, status = ?
        WHERE id = ?
    ''', (
        updated_info.get('name'),
        updated_info.get('email'),
        updated_info.get('status'),
        id
    ))
    conn.commit()
    conn.close()

def delete_interviewee_by_id(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM interviewees WHERE id = ?', (id,))
    conn.commit()
    conn.close()