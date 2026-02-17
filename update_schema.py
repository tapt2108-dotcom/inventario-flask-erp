import sqlite3
import os

# Path to database
# Assuming instance/inventory.db
DB_PATH = os.path.join('instance', 'inventory.db')

def update_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. It will be created when running the app.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # List of columns to check and their types
    # Format: (column_name, column_type)
    columns_to_check = [
        ('part_number', 'VARCHAR(50)'),
        ('manufacturer', 'VARCHAR(50)'),
        ('compatibility', 'TEXT'),
        ('location', 'VARCHAR(50)'),
        ('min_stock', 'INTEGER DEFAULT 0'),
        ('brand', 'VARCHAR(50)'),
        ('vehicle_type', 'VARCHAR(20)'),
        ('price_usd', 'FLOAT DEFAULT 0.0'),
        ('category_id', 'INTEGER'),
        ('is_active', 'BOOLEAN DEFAULT 1')
    ]

    print("Checking for missing columns in 'product' table...")
    for col_name, col_definition in columns_to_check:
        try:
            cursor.execute(f"SELECT {col_name} FROM product LIMIT 1")
        except sqlite3.OperationalError:
            print(f"Adding '{col_name}' column to product...")
            try:
                cursor.execute(f"ALTER TABLE product ADD COLUMN {col_name} {col_definition}")
            except sqlite3.OperationalError as e:
                print(f"Error adding {col_name}: {e}")

    # 2. Add InventoryMovement table
    print("Creating inventory_movement table if not exists...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_movement (
        id INTEGER PRIMARY KEY,
        product_id INTEGER NOT NULL,
        type VARCHAR(20) NOT NULL,
        quantity INTEGER NOT NULL,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        description VARCHAR(200),
        user_id INTEGER,
        FOREIGN KEY(product_id) REFERENCES product(id),
        FOREIGN KEY(user_id) REFERENCES user(id)
    )
    """)
    
    conn.commit()
    conn.close()
    print("Schema update completed.")

if __name__ == '__main__':
    update_schema()
