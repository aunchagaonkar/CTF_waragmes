#!/usr/bin/env python3

import os
import sys
import subprocess
import threading
import time
import re
import requests
from threading import Semaphore

RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
BOLD = "\033[1m"

total_levels = 10
user_file_path = os.path.expanduser("~/.ctf_user")
sem = Semaphore(2)
levels_pulled = 0
loading_done = False

BACKEND_URL = "http://localhost:3000"
BACKEND_URL = "https://ctf-backend-5yhk.onrender.com"

def get_username():
    """Get or prompt for username, save in ~/.ctf_user"""
    if os.path.isfile(user_file_path):
        with open(user_file_path, "r") as f:
            username = f.read().strip()
            if username:
                print(f"{BOLD}{YELLOW}Welcome back, {username}!{RESET}")
                return username
    username = ""
    while not username:
        username = input(f"{BOLD}{MAGENTA}Enter your CTF username: {RESET}").strip()
    with open(user_file_path, "w") as f:
        f.write(username)
    print(f"{BOLD}{YELLOW}Your username is set to {username}.{RESET}")
    return username

def check_internet():
    try:
        subprocess.check_call(["ping", "-c", "2", "google.com"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{BOLD}{GREEN}Internet is working! Great.{RESET}")
        return True
    except subprocess.CalledProcessError:
        return False

def are_you_sudo():
    return os.geteuid() == 0

def get_os():
    if sys.platform.startswith("linux"):
        try:
            with open("/etc/os-release") as f:
                lines = f.read().lower()
                if "ubuntu" in lines: return "Ubuntu"
                if "debian" in lines: return "Debian"
                if "centos" in lines: return "CentOS"
                if "red hat" in lines: return "RHEL"
                if "fedora" in lines: return "Fedora"
                if "arch" in lines: return "Arch"
        except Exception: pass
    elif sys.platform == "darwin":
        return "MacOS"
    return "Unknown"

def restart_docker():
    os_type = get_os()
    if os_type == "MacOS":
        result = subprocess.call("brew services restart docker > /dev/null 2>&1", shell=True)
        if result == 0:
            print(f"{BOLD}{GREEN}Docker was successfully restarted using brew!{RESET}")
            return True
    elif os_type in ["Ubuntu", "Debian", "CentOS", "Fedora", "RHEL", "Arch"]:
        result = subprocess.call("systemctl restart docker > /dev/null 2>&1", shell=True)
        if result == 0:
            print(f"{BOLD}{GREEN}Docker was successfully restarted{RESET}")
            return True
    else:
        print(f"{BOLD}{RED}Unsupported OS. Cannot restart Docker automatically.{RESET}")
        return False
    return False

def check_and_get_docker():
    is_docker_ok = subprocess.call("docker images > /dev/null 2>&1", shell=True)
    if is_docker_ok == 0:
        print(f"{BOLD}{BLUE}Docker already exists!{RESET}")
        return True
    if restart_docker():
        return True
    print(f"{BOLD}{YELLOW}Docker is not installed. Attempting installation...{RESET}")
    os_type = get_os()
    install_status = -1
    if os_type in ["Ubuntu", "Debian"]:
        install_status = subprocess.call("apt update && apt install -y docker.io curl", shell=True)
    elif os_type in ["CentOS", "RHEL"]:
        install_status = subprocess.call("yum install -y docker curl", shell=True)
    elif os_type == "Fedora":
        install_status = subprocess.call("dnf install -y docker curl", shell=True)
    else:
        print("Unsupported OS. Please install Docker manually.")
        return False
    if install_status == 0:
        print(f"{BOLD}{GREEN}Docker installation successful!{RESET}")
        return restart_docker()
    print("Docker installation failed. Please install manually or rerun the script.")
    return False

def loader_animation():
    global loading_done, levels_pulled
    spinner = ['|', '/', '-', '\\']
    i = 0
    while not loading_done:
        progress = (levels_pulled / total_levels) * 100
        bar_width = 30
        pos = int(levels_pulled * bar_width / total_levels)
        bar = "#" * pos + "-" * (bar_width - pos)
        print(f"\r[{bar}] {progress:.1f}% {spinner[i%4]} ({levels_pulled}/{total_levels}) ", end="", flush=True)
        i += 1
        time.sleep(0.2)
    print("\rAll levels pulled successfully!")

def pull_level(level):
    global levels_pulled
    tag = f"warg{level}"
    docker_image = f"ghcr.io/walchand-linux-users-group/wildwarrior44/wargame_finals:{tag}"
    for attempts in range(3):
        get_level = f"docker pull {docker_image} > /dev/null 2>&1"
        exit_status = subprocess.call(get_level, shell=True)
        if exit_status == 0:
            levels_pulled += 1
            return True
        time.sleep(3)
    return False

def pull_level_thread(level):
    sem.acquire()
    pull_level(level)
    sem.release()

def pull_levels():
    global loading_done, levels_pulled
    if not restart_docker():
        print("Error restarting Docker. Exiting...")
        return False
    print("Getting levels...! Patience is the key.")
    loading_done = False
    levels_pulled = 0
    loader_thread = threading.Thread(target=loader_animation)
    loader_thread.start()
    threads = []
    for i in range(1, total_levels+1):
        t = threading.Thread(target=pull_level_thread, args=(i,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    loading_done = True
    loader_thread.join()
    return True

def setup():
    if not are_you_sudo():
        print(f"{BOLD}{RED}Run the script with sudo!{RESET}")
        return 1
    os.system("clear")
    if not check_internet():
        print(f"{BOLD}{RED}Please check your internet connection.{RESET}")
        return 1
    if not check_and_get_docker():
        print(f"{BOLD}Error getting docker!{RESET}")
        return 1
    if not pull_levels():
        print(f"{BOLD}Error pulling levels!{RESET}")
        return 1
    os.system("clear")
    return 0

def check_file():
    if os.path.isfile(user_file_path):
        with open(user_file_path, "r") as f:
            if f.read().strip():
                print("Setup already performed!")
                return True
        return False
    return False

def get_current_level(user_id):
    """Fetch the current level from backend for the specific user."""
    try:
        resp = requests.get(f"{BACKEND_URL}/getLevel", params={"userId": user_id})
        if resp.status_code == 200:
            return resp.json().get("level", 1)
    except Exception as e:
        print(f"Could not connect to backend: {e}")
    return -1

def print_section_header(title):
    print(f"{BOLD}{MAGENTA}┌──────────────────────────────────────┐{RESET}")
    print(f"{BOLD}{MAGENTA}│ {title}{RESET}{BOLD}{MAGENTA}{' ' * (38 - len(title) - 1)}│{RESET}")
    print(f"{BOLD}{MAGENTA}└──────────────────────────────────────┘{RESET}")

def submit_flag(flag, user_id):
    """Submit flag to backend for the specific user."""
    try:
        resp = requests.post(f"{BACKEND_URL}/checkFlag", json={"flag": flag, "userId": user_id})
        if resp.status_code == 200:
            result = resp.json()
            return result['correct'], result['newLevel']
        else:
            print("Error submitting flag. Backend error.")
            return False, None
    except Exception as e:
        print(f"Could not connect to backend: {e}")
        return False, None

def reset_user(user_id):
    """Reset user progress."""
    try:
        resp = requests.post(f"{BACKEND_URL}/resetUser", json={"userId": user_id})
        if resp.status_code == 200:
            print(f"{YELLOW}{BOLD}Progress reset to level 1!{RESET}")
            return True
        else:
            print(f"{RED}Failed to reset progress. Backend error.{RESET}")
            return False
    except Exception as e:
        print(f"{RED}Failed to reset progress: {e}{RESET}")
        return False

def delete_user(user_id):
    """Delete user from backend and remove local file."""
    try:
        resp = requests.post(f"{BACKEND_URL}/deleteUser", json={"userId": user_id})
        if resp.status_code == 200 and resp.json().get("deleted"):
            print(f"{RED}{BOLD}User '{user_id}' deleted! Exiting...{RESET}")
            if os.path.isfile(user_file_path):
                os.remove(user_file_path)
            return True
        else:
            print("Error deleting user. Backend error.")
            return False
    except Exception as e:
        print(f"Could not connect to backend: {e}")
        return False

def interactive_level_shell(level_name, level_num, user_id):
    # Start docker container if not already running
    check_container = f"docker ps -a --format '{{{{.Names}}}}' | grep -w {level_name} > /dev/null 2>&1"
    container_exists = subprocess.call(check_container, shell=True)
    tag = f"warg{level_num}"
    docker_image = f"ghcr.io/walchand-linux-users-group/wildwarrior44/wargame_finals:{tag}"
    if container_exists != 0:
        level_string = (
            f"docker run -dit --hostname {user_id} --user root --name {level_name} "
            f"{docker_image} /bin/bash > /dev/null 2>&1"
        )
        exit_code = subprocess.call(level_string, shell=True)
        if exit_code != 0:
            print("Failed to start container. Exiting...")
            return False
    print_section_header(f"Welcome {user_id}, to CTF Level {level_num}")
    print(f"{GREEN}{BOLD}Submit the flag using 'submit FLAG{{...}}' below.{RESET}")
    print(f"{GREEN}{BOLD}Type 'attach' to open your Docker shell. Type 'exit' to quit this level session.{RESET}")
    # print(f"{YELLOW}{BOLD}Type 'delete' to delete your CTF account and exit permanently.{RESET}")

    while True:
        try:
            user_input = input(f"{BOLD}{MAGENTA}ctf-{level_num}>{RESET} ").strip()
        except EOFError:
            break
        if user_input.lower().startswith("submit "):
            flag = user_input[7:].strip()
            correct, new_level = submit_flag(flag, user_id)
            if correct:
                print(f"{GREEN}{BOLD}Correct flag! Level up!{RESET}")
                # Remove container
                remove_container = f"docker rm -f {level_name} > /dev/null 2>&1"
                subprocess.call(remove_container, shell=True)
                return new_level
            else:
                print(f"{RED}{BOLD}Incorrect flag. Try again.{RESET}")
        elif user_input.lower() == "attach":
            attach_command = f"docker start {level_name} > /dev/null 2>&1 && docker exec -it {level_name} bash"
            os.system(attach_command)
        elif user_input.lower() == "restart":
            if reset_user(user_id):
                subprocess.call(f"docker rm -f {level_name} > /dev/null 2>&1", shell=True)
                return 1  # Restart from level 1
        elif user_input.lower() == "delete":
            if delete_user(user_id):
                sys.exit(0)
            else:
                print(f"{RED}Failed to delete user. Try again or contact support.{RESET}")
        elif user_input.lower() == "exit":
            print("Exiting current level session.")
            return level_num
        else:
            print("Unknown command. Use 'submit FLAG{{...}}', 'attach', 'restart', 'delete', or 'exit'.")

def main():
    global total_levels
    if len(sys.argv) > 1 and sys.argv[1] == "-r":
        print_section_header("Resetting User....")
        print("User reset is disabled in this version.")
        return
    if not check_file():
        if setup() == 1:
            return
    user_id = get_username()
    print(f"{GREEN}{BOLD}Welcome, {user_id}! Preparing your game session...{RESET}")
    current_level = get_current_level(user_id)
    if current_level == -1:
        print(f"{BOLD}Either the backend is down or there is issue in the database{RESET}")
        return
    while current_level <= total_levels:
        os.system("clear")
        level_name = f"ctf{current_level}"
        new_level = interactive_level_shell(level_name, current_level, user_id)
        if new_level is None:
            break
        if new_level > current_level:
            current_level = new_level
        else:
            break
    # Only print congratulations if actually completed all levels
    if current_level > total_levels:
        print(f"{BOLD}{GREEN}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{BOLD}{GREEN}  🎉 Congratulations! You completed the CTF! 🎉{RESET}")
        print(f"{BOLD}{GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

    else:
        print(f"{BOLD}{GREEN}\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{BOLD}{GREEN}                    Try Again                    {RESET}")
        print(f"{BOLD}{GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

    # print(f"File path: {user_file_path}")

if __name__ == "__main__":
    main()