import sqlite3
import hashlib
import os

def init_db():
    if os.path.exists('database.db'):
        os.remove('database.db')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Table users
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user'
    )
    ''')
    
    # Table data
    cursor.execute('''
    CREATE TABLE data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        user_id INTEGER
    )
    ''')
    
    # Utilisateurs
    password_hash = hashlib.md5('password123'.encode()).hexdigest()
    users = [
        ('admin', password_hash, 'admin'),
        ('user1', password_hash, 'user'),
        ('test', password_hash, 'user')
    ]
    cursor.executemany('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', users)
    
    # Données
    data_entries = [
        ('Server Stats', 'CPU: 45%, RAM: 2.3/4GB', 1),
        ('User Activity', '5 users online', 1),
        ('Backup Status', 'Last backup: 2024-01-15', 2),
        ('Security Log', 'No threats detected', 3)
    ]
    cursor.executemany('INSERT INTO data (title, content, user_id) VALUES (?, ?, ?)', data_entries)
    
    conn.commit()
    conn.close()
    print("✅ Base de données créée!")

if __name__ == '__main__':
    init_db()
