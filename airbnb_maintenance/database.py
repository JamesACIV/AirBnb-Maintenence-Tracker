import sqlite3
from .config import DB_PATH

def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Properties table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            company TEXT,
            phone TEXT,
            email TEXT,
            service_type TEXT
        )
    ''')
    
    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER,
            contact_id INTEGER,
            description TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            cost REAL DEFAULT 0,
            payment_status TEXT DEFAULT 'unpaid',
            completion_status TEXT DEFAULT 'incomplete',
            recurring TEXT DEFAULT 'no',
            recurrence_interval TEXT,
            notes TEXT,
            FOREIGN KEY (property_id) REFERENCES properties (id),
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")
