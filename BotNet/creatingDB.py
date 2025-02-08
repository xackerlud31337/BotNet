import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect('bots.db')

# Create a cursor object
cursor = conn.cursor()

# Create the "bots" table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS bots (
        id INTEGER PRIMARY KEY,
        ip TEXT,
        last_seen TEXT DEFAULT (datetime('now', 'localtime'))
    )
""")

# Commit and close the connection
conn.commit()
conn.close()

print("Database 'bots.db' created successfully!")
