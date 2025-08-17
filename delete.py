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
