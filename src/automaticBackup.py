import tkinter as tk
from tkinter import filedialog
import shutil
import time
import threading

def backup_files():
    source_folder = source_var.get()
    destination_folder = destination_var.get()
    interval = int(interval_var.get())
    num_copies_str = num_copies_var.get()
    
    # If num_copies_str is empty or not a valid integer, set num_copies to None (infinite copies)
    try:
        num_copies = int(num_copies_str)
    except ValueError:
        num_copies = None

    if not source_folder or not destination_folder:
        status_var.set("Error: Source or Destination folder is not set!")
        return

    def backup_thread():
        try:
            copies_made = 0
            while num_copies is None or copies_made < num_copies:
                # Copy the contents of the source folder to the destination folder
                shutil.copytree(source_folder, destination_folder, dirs_exist_ok=True)
                copies_made += 1
                status_var.set(f"Files copied successfully ({copies_made} / {num_copies_str if num_copies else '∞'}).")
                # Wait for the specified time interval
                time.sleep(interval)
        except Exception as e:
            status_var.set(f"An error occurred: {e}")

    # Create a new thread for the backup operation
    backup_thread = threading.Thread(target=backup_thread)
    backup_thread.daemon = True  # Make the thread a daemon thread so it stops when the main thread stops
    backup_thread.start()

def browse_source():
    folder_path = filedialog.askdirectory()
    if folder_path:
        source_var.set(folder_path)

def browse_destination():
    folder_path = filedialog.askdirectory()
    if folder_path:
        destination_var.set(folder_path)

# Create the main window
root = tk.Tk()
root.title("Automatic Backup")

# Load the icon file
icon_path = "backup.ico"

# Set the icon
root.iconbitmap(icon_path)

# Disable resizing (maximize button)
root.resizable(False, False)

# Variables to store source, destination folder paths, time interval, and number of copies
source_var = tk.StringVar()
destination_var = tk.StringVar()
interval_var = tk.StringVar(value="10")  # Default interval is 10 seconds
num_copies_var = tk.StringVar(value="")  # Default is empty (infinite copies)
status_var = tk.StringVar()

# Source folder entry and browse button
tk.Label(root, text="Source Folder:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=source_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_source).grid(row=0, column=2, padx=5, pady=5)

# Destination folder entry and browse button
tk.Label(root, text="Destination Folder:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=destination_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_destination).grid(row=1, column=2, padx=5, pady=5)

# Time interval entry
tk.Label(root, text="Time Interval (seconds):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=interval_var, width=10).grid(row=2, column=1, padx=5, pady=5)

# Number of copies entry
tk.Label(root, text="Number of Copies (empty for infinite):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=num_copies_var, width=10).grid(row=3, column=1, padx=5, pady=5)

# Backup button
tk.Button(root, text="Start Backup", command=backup_files).grid(row=4, column=1, padx=5, pady=10)

# Status label
status_label = tk.Label(root, textvariable=status_var)
status_label.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

# Run the GUI
root.mainloop()
