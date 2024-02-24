import os
import shutil
import tkinter as tk
from tkinter import filedialog, ttk
import threading
import logging

# Initialize logging
logging.basicConfig(level=logging.ERROR)

# Function to merge folders
def merge_folders(folder_path):
    try:
        # Get list of folders in the specified directory
        folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]

        # Dictionary to store common folder names and their corresponding numbered folders
        common_folders = {}

        # Iterate through each folder
        for folder in folders:
            # Extract common part of the folder name
            parts = folder.split(' (')
            common_name = parts[0]

            # Check if there is a number part in the folder name
            if len(parts) > 1:
                try:
                    # Extract the number part
                    number_part = parts[-1].split(')')[0]
                    number = int(number_part)
                except ValueError:
                    # Skip folders with non-numeric number parts
                    continue
            else:
                number = 0

            # Check if common part exists in the dictionary
            if common_name in common_folders:
                # Add folder to existing common folder
                common_folders[common_name].append((folder, number))
            else:
                # Create new entry for common folder
                common_folders[common_name] = [(folder, number)]

        # Iterate through common folders and merge them
        for common_name, folders_list in common_folders.items():
            if len(folders_list) > 1:
                # Determine the highest numbered folder
                highest_folder = max(folders_list, key=lambda x: x[1])
                main_folder = highest_folder[0].split(' (')[0]

                # Move contents of numbered folders to main folder
                for folder, _ in folders_list:
                    if folder != main_folder:
                        folder_path = os.path.join(folder_path, folder)
                        main_folder_path = os.path.join(folder_path, main_folder)
                        if not os.path.exists(main_folder_path):
                            os.makedirs(main_folder_path)
                        # Move contents of numbered folder to main folder
                        for item in os.listdir(folder_path):
                            # Check if item is a file
                            item_path = os.path.join(folder_path, item)
                            if os.path.isfile(item_path):
                                # Check if item is not an image or video
                                if not is_image_or_video(item):
                                    continue
                            shutil.move(item_path, os.path.join(main_folder_path, item))
                        # Delete numbered folder if it's empty
                        if not os.listdir(folder_path):
                            os.rmdir(folder_path)

        # Delete empty folders
        delete_empty_folders(folder_path)
    except Exception as e:
        logging.error(f"An error occurred during folder merging: {str(e)}")

# Function to delete empty folders
def delete_empty_folders(folder_path):
    try:
        # Check if folder exists before listing its contents
        if os.path.exists(folder_path):
            # Get list of folders in the specified directory
            folders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]
        else:
            return
    except FileNotFoundError:
        # If the folder does not exist, return
        return

    # Iterate through each folder
    for folder in folders:
        folder_path = os.path.join(folder_path, folder)
        try:
            # Recursively delete empty folders
            delete_empty_folders(folder_path)
        except FileNotFoundError:
            # If the folder does not exist, continue
            continue
        # Check if folder is empty and delete it
        if not os.listdir(folder_path):
            os.rmdir(folder_path)

# Function to check if a file is an image or video
def is_image_or_video(filename):
    # Check if file extension is among common image or video extensions
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    video_extensions = ['.avi', '.mp4', '.mkv', '.mov', '.wmv']
    _, ext = os.path.splitext(filename)
    return ext.lower() in image_extensions or ext.lower() in video_extensions

# Function to handle folder selection
def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_var.set(folder_selected)

# Function to merge folders and update progress
def merge_and_show_progress():
    folder_path = folder_var.get()
    progress_bar.start()
    threading.Thread(target=merge_folders, args=(folder_path,)).start()

# GUI Setup
root = tk.Tk()
root.title("Folder Merger")
root.configure(bg="black")  # Set background color to black

# Main Frame
main_frame = ttk.Frame(root, style="Dark.TFrame")  # Use a custom dark theme for the frame
main_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

# Configure resizing behavior
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Folder Selection
select_button = ttk.Button(main_frame, text="Select Folder", command=select_folder)
select_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

folder_var = tk.StringVar()
folder_var.set("No folder selected")
folder_label = ttk.Label(main_frame, textvariable=folder_var)
folder_label.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Merge Button
merge_button = ttk.Button(main_frame, text="Merge", command=merge_and_show_progress)
merge_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

# Progress Bar
progress_bar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='indeterminate')
progress_bar.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

# Resize fonts when the window is resized
def resize_fonts(event):
    width = event.width
    new_size = int(width / 40)  # Adjust the divisor to control text scaling
    style = ttk.Style()
    style.configure('TButton', font=('TkDefaultFont', new_size))
    style.configure('TLabel', font=('TkDefaultFont', new_size))

root.bind("<Configure>", resize_fonts)

root.mainloop()
