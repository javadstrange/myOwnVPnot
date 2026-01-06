import os
import re
import sys
import subprocess

# --- CONFIGURATION ---
IGNORE_FILES = ['.git', 'README.md', 'update_ip.py', '.gitignore']
# ---------------------

def update_configs(new_ip):
    # Regex to find IP addresses (e.g., 192.168.1.1)
    ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')

    current_dir = os.getcwd()
    files_changed = False

    for filename in os.listdir(current_dir):
        if filename in IGNORE_FILES or filename.startswith('.'):
            continue
        if os.path.isdir(filename):
            continue

        print(f"Checking {filename}...", end=" ")

        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if file has vless/vmess
            if 'vless://' in content or 'vmess://' in content:
                # Replace the OLD IP with the NEW IP
                new_content = ip_pattern.sub(new_ip, content)

                if new_content != content:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"UPDATED to {new_ip}")
                    files_changed = True
                else:
                    print("No change needed.")
            else:
                print("Ignored (not a config).")

        except Exception as e:
            print(f"Error: {e}")
            
    return files_changed

def git_push(new_ip):
    print("\nStarting GitHub upload...")
    try:
        # Add all files
        subprocess.run(["git", "add", "."], check=True, shell=True)
        
        # Commit
        subprocess.run(["git", "commit", "-m", f"Update IP to {new_ip}"], check=True, shell=True)
        
        # Push
        result = subprocess.run(["git", "push"], check=True, shell=True)
        if result.returncode == 0:
            print("--------------------------------------")
            print("SUCCESS! Your GitHub files are updated.")
            print("--------------------------------------")
            
    except subprocess.CalledProcessError as e:
        print("\nERROR during Git Push.")
        print("If this is your first time, a window might have popped up asking for login.")
        print("If asked for a password in the console, PASTE YOUR TOKEN (ghp_...), not your account password.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Ask for IP if not provided in command line
        new_ip_arg = input("Enter the new IP address: ").strip()
    else:
        new_ip_arg = sys.argv[1]

    # Simple validation
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', new_ip_arg):
        print("Error: Invalid IP format.")
        sys.exit(1)

    if update_configs(new_ip_arg):
        git_push(new_ip_arg)
    else:
        print("\nNo files needed changing. Git push skipped.")