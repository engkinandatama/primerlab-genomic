# 🚀 PrimerLab WSL Quickstart Guide

This guide covers the complete setup process for running PrimerLab on Windows via WSL (Windows Subsystem for Linux).

---

## 🛠️ 1. Prerequisites

Ensure you have:
1.  **WSL2 Installed**: Run `wsl --install` in PowerShell if you haven't.
2.  **Ubuntu Distro**: Default for WSL.
3.  **Python 3.10+**: Usually pre-installed on modern Ubuntu.

---

## 📂 2. Project Setup (First Time Only)

### Step A: Access the Project
Your Windows drives are mounted under `/mnt/`.
If your project is in `E:\Project\primerlab-genomic`, access it like this:

```bash
# Create the directory structure if it doesn't exist (optional)
mkdir -p /mnt/e/Project

# Navigate to the project folder
cd /mnt/e/Project/primerlab-genomic
```

### Step B: Set Up Virtual Environment (Venv)
We recommend creating the `venv` in your Linux home directory (`~`) to avoid file permission issues and slowdowns associated with the Windows filesystem.

```bash
# 1. Install venv module (if missing)
# Note: Using python3-venv ensures compatibility with your system's default Python (e.g., 3.12 on Ubuntu 24.04)
sudo apt update && sudo apt install python3-venv -y

# 2. Create the venv in your home folder
python3 -m venv ~/primerlab_venv

# 3. Activate it
source ~/primerlab_venv/bin/activate
```

### Step C: Install Dependencies
With the venv activated (you should see `(primerlab_venv)` in your prompt):

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Install the project in editable mode
pip install -e .
```

---

## 🏃 3. Daily Usage

Every time you open a new terminal to work on PrimerLab:

1.  **Go to the project:**
    ```bash
    cd /mnt/e/Project/primerlab-genomic
    ```

2.  **Activate the environment:**
    ```bash
    source ~/primerlab_venv/bin/activate
    ```

3.  **Run commands:**
    ```bash
    # Run qPCR Workflow
    python3 -m primerlab.cli.main run qpcr --config test_qpcr.yaml
    ```

---

## 🧹 4. Cleanup (Removing Old Folders)

If you renamed your folder from `PrimerLab` to `primerlab-genomic` and want to remove the old empty/unused folder:

```bash
# Check if the old folder exists
ls -ld /mnt/e/Project/PrimerLab

# Remove it (WARNING: This deletes it permanently)
rm -rf /mnt/e/Project/PrimerLab
```

---

## ❓ Troubleshooting

### "Stuck" or Hanging Process
If the program hangs while designing primers:
- The default timeout is now **30 seconds**.
- If it times out, try relaxing constraints in your config file (e.g., widen Tm range).

### "ModuleNotFoundError"
- Ensure you activated the venv: `source ~/primerlab_venv/bin/activate`
- Ensure you installed the package: `pip install -e .`
