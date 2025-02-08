# BotNet Project

## Overview
This project is a simple botnet implementation using Python and Flask. It includes a command and control (C2) server, bot instances, and a dashboard for managing the bots.

## Project Structure
- `BotNet/bot.py`: Contains the bot instance code that will fill up the database (create the bots).
- `BotNet/server.py`: Contains the Flask server code.
- `BotNet/templates/dashboard.html`: Contains the HTML template for the dashboard.
- `console_2.sql`: Contains SQL queries for managing the database.

## Setup
1. Clone the repository.
2. Create a virtual environment:
    ```sh
    python -m venv venv
    ```
3. Activate the virtual environment:
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```
    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
4. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage
1. Initialize the database:
    ```sh
    python BotNet/server.py
    ```
2. Start the Flask server:
    ```sh
    python BotNet/server.py
    ```
3. Start the bot instances:
    ```sh
    python BotNet/bot.py
    ```

## License
This project is licensed under the MIT License.