---
description: How to install and set up WSL 2 on Windows
---

# Installing WSL 2 (Windows Subsystem for Linux)

WSL 2 allows you to run a full Linux environment directly on Windows, which is ideal for bioinformatics tools.

## Step 1: Open PowerShell as Administrator

1.  Press the **Windows Key**.
2.  Type **PowerShell**.
3.  Right-click on "Windows PowerShell" and select **Run as Administrator**.
4.  Click **Yes** if asked for permission.

## Step 2: Run the Install Command

In the Administrator PowerShell window, type the following command and press Enter:

```powershell
wsl --install
```

**What this does:**
*   Enables the required Windows features (WSL and Virtual Machine Platform).
*   Downloads the latest Linux kernel.
*   Installs **Ubuntu** as the default Linux distribution.

## Step 3: Restart Your Computer

Once the command finishes, you **MUST restart your computer** to complete the installation.

## Step 4: Set Up Ubuntu

1.  After restarting, the installation will resume automatically. A terminal window will open.
2.  If it doesn't open, search for **Ubuntu** in the Start menu and open it.
3.  You will be asked to create a **Username** and **Password** for your Linux system.
    *   *Note: When typing the password, nothing will appear on the screen. This is normal security behavior. Just type it and press Enter.*

## Step 5: Update Linux (Optional but Recommended)

Once you are inside the Ubuntu terminal (you'll see a prompt like `username@computername:~$`), run these commands to update your tools:

```bash
sudo apt update && sudo apt upgrade -y
```

(Enter your password when asked).

## Step 6: Verify Installation

To check if everything is correct, open a new PowerShell window (normal or admin) and run:

```powershell
wsl --list --verbose
```

You should see `Ubuntu` listed with `Running` or `Stopped` and VERSION `2`.

---

## Troubleshooting

*   **"wsl is not recognized..."**: Make sure you are on a recent version of Windows 10 (version 2004+) or Windows 11.
*   **Virtualization error**: Ensure "Virtualization" is enabled in your computer's BIOS settings.
