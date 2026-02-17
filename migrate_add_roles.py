"""
Proper migration script to add role column to existing database.
This uses raw SQL to alter the table structure.
"""
import sqlite3
import os

def migrate_database():
    db_path = 'instance/inventory.db'
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run the application first to create the database.")
        return
    
    print(f"Migrating database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if role column already exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'role' in columns:
            print("SUCCESS: Role column already exists!")
        else:
            print("Adding role column to user table...")
            cursor.execute("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'seller' NOT NULL")
            print("SUCCESS: Role column added successfully!")
        
        # Update existing users based on is_admin
        print("Migrating existing user roles...")
        cursor.execute("UPDATE user SET role = 'admin' WHERE is_admin = 1")
        admin_count = cursor.rowcount
        cursor.execute("UPDATE user SET role = 'seller' WHERE is_admin = 0 OR is_admin IS NULL")
        seller_count = cursor.rowcount
        
        print(f"  - Set {admin_count} users as 'admin'")
        print(f"  - Set {seller_count} users as 'seller'")
        
        # Check if user_id column exists in sale table
        cursor.execute("PRAGMA table_info(sale)")
        sale_columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' in sale_columns:
            print("SUCCESS: Sale.user_id column already exists!")
        else:
            print("Adding user_id column to sale table...")
            cursor.execute("ALTER TABLE sale ADD COLUMN user_id INTEGER")
            print("SUCCESS: Sale.user_id column added successfully!")
        
        conn.commit()
        
        # Display final user roles
        print("\nCurrent user roles:")
        cursor.execute("SELECT username, role FROM user")
        for username, role in cursor.fetchall():
            print(f"  - {username}: {role}")
        
        print("\nMigration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\nERROR: Migration failed: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
