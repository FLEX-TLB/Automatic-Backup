import tkinter as tk
from tkinter import filedialog
import shutil
import threading
import os

backup_event = threading.Event()
backup_process = None

def validate_interval_input():
    interval = interval_var.get()
    if not interval.isdigit() or int(interval) <= 0:
        status_var.set("Error: Time interval must be a positive integer.")
        return False
    return True

def validate_copies_input():
    num_copies = num_copies_var.get()
    if num_copies and (not num_copies.isdigit() or int(num_copies) <= 0):
        status_var.set("Error: Number of copies must be a positive integer or empty.")
        return False
    return True

def backup_files():
    if not validate_interval_input() or not validate_copies_input():
        return
    global backup_process
    global backup_data
    global backup_method
    source_folder = source_var.get()
    interval = int(interval_var.get())
    num_copies_str = num_copies_var.get()

    try:
        num_copies = int(num_copies_str)
    except ValueError:
        num_copies = None

    if not source_folder or not destination_var.get():
        status_var.set("Error: Source or Destination folder is not set!")
        return

    if backup_process and backup_process.is_alive():
        status_var.set("Cannot start backup. There is an active process.")
        return

    backup_data = {
        "source_folder": source_folder,
        "destination_folder": destination_var.get(),
        "interval": interval,
        "num_copies": num_copies
    }
    backup_method = method

    def backup_thread():
        try:
            global backup_process
            copies_made = 0
            while not backup_event.is_set() and (num_copies is None or copies_made < num_copies):
                if backup_method == "Override":
                    destination_folder = os.path.basename(backup_data["source_folder"])
                else:
                    destination_folder = f"{os.path.basename(backup_data['source_folder'])}_{copies_made + 1}"
                full_destination_folder = os.path.join(backup_data["destination_folder"], destination_folder)
                if backup_method == "Override" and os.path.exists(full_destination_folder):
                    shutil.rmtree(full_destination_folder)
                shutil.copytree(backup_data["source_folder"], full_destination_folder, dirs_exist_ok=True)
                copies_made += 1
                status_var.set(f"Backup {copies_made} created at: {full_destination_folder}")
                if interval > 0:
                    backup_event.wait(interval)

        except Exception as e:
            status_var.set(f"An error occurred: {e}")
        finally:
            if num_copies is not None and copies_made == num_copies:
                status_var.set("Backup finished")
            elif backup_event.is_set():
                status_var.set("Process terminated")
            backup_event.clear()

    backup_process = threading.Thread(target=backup_thread)
    backup_process.daemon = True
    backup_process.start()

def terminate_process():
    global backup_process
    if backup_process and backup_process.is_alive():
        backup_event.set()
        status_var.set("Process termination requested")
    else:
        status_var.set("No active process to terminate")

def browse_source():
    folder_path = filedialog.askdirectory()
    if folder_path:
        source_var.set(folder_path)

def browse_destination():
    folder_path = filedialog.askdirectory()
    if folder_path:
        destination_var.set(folder_path)

def set_backup_method(value):
    global method
    method = value

root = tk.Tk()
root.title("Automatic Backup")

icon_path = "backup.ico"
root.after(100, lambda: root.iconbitmap(icon_path))
root.resizable(False, False)

source_var = tk.StringVar()
destination_var = tk.StringVar()
interval_var = tk.StringVar(value="10")
num_copies_var = tk.StringVar(value="")

tk.Label(root, text="Source Folder:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=source_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_source).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Destination Folder:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=destination_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_destination).grid(row=1, column=2, padx=5, pady=5)

tk.Label(root, text="Time Interval (seconds):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=interval_var, width=10).grid(row=2, column=1, padx=5, pady=5)

tk.Label(root, text="Number of Copies (empty for infinite):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
tk.Entry(root, textvariable=num_copies_var, width=10).grid(row=3, column=1, padx=5, pady=5)

tk.Label(root, text="Backup Method:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
method = tk.StringVar(value="Sequential")
tk.Radiobutton(root, text="Sequential", variable=method, value="Sequential", command=lambda: set_backup_method("Sequential")).grid(row=4, column=1, padx=5, pady=5, sticky="w")
tk.Radiobutton(root, text="Override", variable=method, value="Override", command=lambda: set_backup_method("Override")).grid(row=4, column=1, padx=5, pady=5, sticky="e")

backup_button = tk.Button(root, text="Start Backup", command=backup_files)
backup_button.grid(row=5, column=0, columnspan=2, padx=(0, 5), pady=10)

terminate_button = tk.Button(root, text="Terminate Process", command=terminate_process)
terminate_button.grid(row=5, column=1, columnspan=2, padx=(5, 90), pady=10)

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var)
status_label.grid(row=6, column=0, columnspan=3, padx=5, pady=5)

root.mainloop()
