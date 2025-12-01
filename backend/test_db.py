import sqlite3
import os

# Change this to YOUR actual database path
db_path = r"C:\Users\Kartik joshi\company_database.db"

print(f"Checking database at: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"\nTables found: {len(tables)}")
    for table in tables:
        print(f"  - {table[0]}")
        
        # Count rows in each table
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"    Rows: {count}")
    
    conn.close()
else:
    print("ERROR: Database file not found!")