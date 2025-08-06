# CTF_waragmes

A Python-based platform for running and playing Capture the Flag (CTF) wargames with an interactive, multi-level challenge system.

---

## Overview

**CTF_waragmes** helps automate and manage CTF-style wargames. The script orchestrates challenge environments (levels) for participants, tracks progress, and provides an interactive experience for solving and submitting flags.

---

## Features

- **Multi-level CTF Structure:** Progress through sequential challenge levels.
- **Interactive CLI:** User-friendly command-line interface with progress bars, colored prompts, and clear instructions.
- **Shell Access:** Attach interactively to each level's environment to solve challenges.
- **Progress Management:** Submit flags to unlock new levels, and use the `restart` command to reset your progress to level 1.
- **Cross-platform:** Supports Linux and MacOS for both players and organizers.
- **Concurrent Setup:** Efficiently prepares all challenge environments in parallel.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/PranavG1203/CTF_waragmes.git
cd CTF_waragmes
```

---

### 2. Install Python Dependencies

All dependencies can be installed with:

```bash
pip install -r requirements.txt
```

---

### 3. Run the Game Script

Run the main script with Python 3:

```bash
python3 play.py
```

---

### 4. Using the Tool

Follow the CLI instructions. Available commands at the prompt:

- `attach` – Open an interactive shell in the current level's environment.
- `submit FLAG{...}` – Submit your flag for the current level.
- `restart` – Reset your progress to level 1. 
- `exit` – Exit the current level session.

_Example session:_
```text
ctf-2> attach
# ...solve the challenge...
ctf-2> submit FLAG{your_flag_here}
Correct flag! Level up!
```

---

## Notes

- **Persistence:** Progress is tracked per session. If you restart the script, your progress may be reset.
- **Customization:** To add or modify levels, edit the relevant Python code and ensure the appropriate challenge environments are available.
- **User ID:** The user is currently hardcoded. You can change it in the source code if needed.

---

## Troubleshooting

- **Permission errors:** Ensure you have the necessary permissions to run the script and access system resources.
- **Unable to progress:** Ensure your submitted flags match the expected format for each level.

---

## Contributing

Pull requests are welcome!  
For suggestions, bug reports, or questions, please open an issue.

---

