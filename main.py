import os
import shutil
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import logging
import queue

# Initialize logging
logging.basicConfig( level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',
                     filename='folder_merger.log', filemode='a' )


# Function to merge folders
def merge_folders(folder_path, progress_var, status_var, progress_queue, stop_event, include_extensions,
                  exclude_extensions, handle_duplicates):
    try:
        # Get all subdirectories in the folder
        subdirs = [d for d in os.listdir( folder_path ) if os.path.isdir( os.path.join( folder_path, d ) )]

        # Create a set of all directories to process
        dirs_to_process = set( os.path.join( folder_path, subdir ) for subdir in subdirs )

        # Process directories recursively
        while dirs_to_process:
            current_dir = dirs_to_process.pop()
            base_name = os.path.basename( current_dir )

            if base_name == folder_path:
                continue

            move_contents( current_dir, folder_path, include_extensions, exclude_extensions, handle_duplicates,
                           stop_event )

            # Add subdirectories to process
            for subdir in os.listdir( current_dir ):
                subdir_path = os.path.join( current_dir, subdir )
                if os.path.isdir( subdir_path ):
                    dirs_to_process.add( subdir_path )

        # Delete empty directories in the original structure
        delete_empty_folders( folder_path )

        status_var.set( "Merging Completed!" )
        messagebox.showinfo( "Success", "Folders merged successfully!" )

    except Exception as e:
        logging.error( f"An error occurred during folder merging: {str( e )}" )
        status_var.set( "Error during merging." )
        messagebox.showerror( "Error", f"An error occurred: {str( e )}" )


# Function to move contents of a directory to a target directory
def move_contents(src_dir, dest_dir, include_extensions, exclude_extensions, handle_duplicates, stop_event):
    if stop_event.is_set():
        return

    try:
        for item in os.listdir( src_dir ):
            item_path = os.path.join( src_dir, item )
            if os.path.isfile( item_path ):
                _, ext = os.path.splitext( item_path )
                if (include_extensions and ext.lower() not in include_extensions) or (
                        exclude_extensions and ext.lower() in exclude_extensions):
                    continue
                if os.path.getsize( item_path ) == 0:
                    os.remove( item_path )
                    continue

                dest_path = os.path.join( dest_dir, item )
                if os.path.exists( dest_path ):
                    if handle_duplicates == 'skip':
                        continue
                    elif handle_duplicates == 'replace':
                        os.remove( dest_path )
                    elif handle_duplicates == 'rename':
                        base, extension = os.path.splitext( item )
                        counter = 1
                        new_dest_path = os.path.join( dest_dir, f"{base}_{counter}{extension}" )
                        while os.path.exists( new_dest_path ):
                            counter += 1
                            new_dest_path = os.path.join( dest_dir, f"{base}_{counter}{extension}" )
                        dest_path = new_dest_path

                shutil.move( item_path, dest_path )
            elif os.path.isdir( item_path ):
                move_contents( item_path, os.path.join( dest_dir, item ), include_extensions, exclude_extensions,
                               handle_duplicates, stop_event )

    except Exception as e:
        logging.error( f"Error moving contents from {src_dir} to {dest_dir}: {str( e )}" )


# Function to delete empty folders
def delete_empty_folders(folder_path):
    for root, dirs, files in os.walk( folder_path, topdown=False ):
        for d in dirs:
            dir_path = os.path.join( root, d )
            try:
                if not os.listdir( dir_path ):
                    os.rmdir( dir_path )
            except Exception as e:
                logging.error( f"Error deleting empty folder {dir_path}: {str( e )}" )


# Function to handle folder selection
def select_folder():
    folder_selected = filedialog.askdirectory( mustexist=False )
    if folder_selected:
        folder_var.set( folder_selected )


# Function to merge folders and update progress
def merge_and_show_progress():
    folder_path = folder_var.get()
    include_extensions = set( include_extensions_var.get().split() )
    exclude_extensions = set( exclude_extensions_var.get().split() )
    handle_duplicates = duplicate_handling_var.get()

    if folder_path == "No folder selected" or not folder_path:
        messagebox.showwarning( "Warning", "Please select a folder." )
        return

    if messagebox.askyesno( "Confirm", "Are you sure you want to start the merge process?" ):
        progress_var.set( 0 )
        status_var.set( "Merging in progress..." )
        stop_event.clear()
        progress_queue = queue.Queue()
        threading.Thread( target=merge_folders, args=(
        folder_path, progress_var, status_var, progress_queue, stop_event, include_extensions, exclude_extensions,
        handle_duplicates) ).start()
        root.after( 100, update_progress, progress_queue )


# Function to update the progress bar
def update_progress(progress_queue):
    try:
        progress = progress_queue.get_nowait()
        progress_var.set( progress )
    except queue.Empty:
        pass
    if status_var.get() != "Merging Completed!" and status_var.get() != "Error during merging.":
        root.after( 100, update_progress, progress_queue )


# Function to cancel the merge operation
def cancel_merge():
    stop_event.set()


# GUI Setup
root = tk.Tk()
root.title( "Folder Merger" )
root.geometry( "800x600" )
root.configure( bg="#2e2e2e" )

style = ttk.Style()
style.theme_use( "clam" )
style.configure( "TFrame", background="#2e2e2e" )
style.configure( "TButton", background="#4a4a4a", foreground="#ffffff", font=("Helvetica", 12) )
style.configure( "TLabel", background="#2e2e2e", foreground="#ffffff", font=("Helvetica", 12) )
style.configure( "TEntry", background="#4a4a4a", foreground="#ffffff", font=("Helvetica", 12) )
style.configure( "TCombobox", background="#4a4a4a", foreground="#ffffff", font=("Helvetica", 12) )
style.configure( "Horizontal.TProgressbar", troughcolor='#4a4a4a', background='#6c6c6c' )

# Main Frame
main_frame = ttk.Frame( root )
main_frame.pack( padx=20, pady=20, fill="both", expand=True )

# Title
title_label = ttk.Label( main_frame, text="Folder Merger", font=("Helvetica", 20, "bold") )
title_label.pack( pady=10 )

# Folder Selection
folder_var = tk.StringVar()
folder_var.set( "No folder selected" )

folder_frame = ttk.Frame( main_frame )
folder_frame.pack( pady=10, fill="x" )

select_button = ttk.Button( folder_frame, text="Select Folder", command=select_folder )
select_button.pack( side="left", padx=(0, 10) )

folder_label = ttk.Label( folder_frame, textvariable=folder_var, relief="sunken" )
folder_label.pack( side="left", fill="x", expand=True )

# File Type Filters
include_extensions_var = tk.StringVar()
exclude_extensions_var = tk.StringVar()

include_extensions_label = ttk.Label( main_frame, text="Include extensions (space-separated):" )
include_extensions_label.pack( pady=5, fill="x" )
include_extensions_entry = ttk.Entry( main_frame, textvariable=include_extensions_var )
include_extensions_entry.pack( pady=5, fill="x" )

exclude_extensions_label = ttk.Label( main_frame, text="Exclude extensions (space-separated):" )
exclude_extensions_label.pack( pady=5, fill="x" )
exclude_extensions_entry = ttk.Entry( main_frame, textvariable=exclude_extensions_var )
exclude_extensions_entry.pack( pady=5, fill="x" )

# Duplicate File Handling
duplicate_handling_var = tk.StringVar( value="skip" )
duplicate_handling_label = ttk.Label( main_frame, text="Handle duplicates:" )
duplicate_handling_label.pack( pady=5, fill="x" )
duplicate_handling_options = ttk.Combobox( main_frame, textvariable=duplicate_handling_var,
                                           values=["skip", "replace", "rename"] )
duplicate_handling_options.pack( pady=5, fill="x" )

# Merge Button
button_frame = ttk.Frame( main_frame )
button_frame.pack( pady=10, fill="x" )

merge_button = ttk.Button( button_frame, text="Merge", command=merge_and_show_progress )
merge_button.pack( side="left", padx=(0, 10) )

cancel_button = ttk.Button( button_frame, text="Cancel", command=cancel_merge )
cancel_button.pack( side="left", padx=(0, 10) )

# Progress Bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar( main_frame, orient=tk.HORIZONTAL, mode='determinate', variable=progress_var )
progress_bar.pack( pady=10, fill="x" )

# Status Label
status_var = tk.StringVar()
status_var.set( "Ready" )
status_label = ttk.Label( main_frame, textvariable=status_var, relief="sunken" )
status_label.pack( pady=5, fill="x" )

# Log Viewer
log_label = ttk.Label( main_frame, text="Log Messages:" )
log_label.pack( pady=5, fill="x" )

log_text = tk.Text( main_frame, height=10, bg="#4a4a4a", fg="#ffffff", state="disabled" )
log_text.pack( pady=5, fill="x" )


# Update log messages in the text widget
def update_log():
    with open( 'folder_merger.log', 'r' ) as log_file:
        log_text.configure( state="normal" )
        log_text.delete( 1.0, tk.END )
        log_text.insert( tk.END, log_file.read() )
        log_text.configure( state="disabled" )
    root.after( 1000, update_log )


update_log()


# Tooltips for better guidance
def create_tooltip(widget, text):
    tooltip = tk.Toplevel( widget )
    tooltip.withdraw()
    tooltip.overrideredirect( True )
    tooltip_label = tk.Label( tooltip, text=text, bg="#333333", fg="#ffffff", relief="solid", borderwidth=1,
                              font=("Helvetica", 10, "normal") )
    tooltip_label.pack()

    def enter(event):
        x, y = widget.winfo_pointerxy()
        tooltip.geometry( f"+{x + 20}+{y + 20}" )
        tooltip.deiconify()

    def leave(event):
        tooltip.withdraw()

    widget.bind( "<Enter>", enter )
    widget.bind( "<Leave>", leave )


create_tooltip( select_button, "Select the folder containing subdirectories to merge." )
create_tooltip( include_extensions_entry, "Specify extensions to include, separated by spaces." )
create_tooltip( exclude_extensions_entry, "Specify extensions to exclude, separated by spaces." )
create_tooltip( duplicate_handling_options, "Choose how to handle duplicate files." )
create_tooltip( merge_button, "Click to start merging subdirectories." )
create_tooltip( cancel_button, "Click to cancel the merging process." )

# Stop event for cancelling the merge operation
stop_event = threading.Event()

root.mainloop()
