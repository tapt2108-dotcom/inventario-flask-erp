"""
Migration script to add LoginAttempt table for security tracking.
This adds a new table without modifying existing tables.
"""
import sqlite3
import os

def migrate_login_attempts():
    db_path = 'instance/inventory.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run the application first to create the database.")
        return
    
    print(f"Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if login_attempt table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='login_attempt'")
        if cursor.fetchone():
            print("SUCCESS: login_attempt table already exists!")
        else:
            print("Creating login_attempt table...")
            cursor.execute("""
                CREATE TABLE login_attempt (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(64) NOT NULL,
                    ip_address VARCHAR(45),
                    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN NOT NULL DEFAULT 0,
                    user_agent VARCHAR(256)
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX ix_login_attempt_username ON login_attempt (username)")
            cursor.execute("CREATE INDEX ix_login_attempt_timestamp ON login_attempt (timestamp)")
            
            print("SUCCESS: login_attempt table created successfully!")
        
        conn.commit()
        print("\nMigration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_login_attempts()
