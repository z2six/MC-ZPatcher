import tkinter as tk
from tkinter import filedialog, ttk, Scrollbar, Menu
from PIL import Image, ImageTk
import os
import subprocess
import json
import shutil
from ModDetailPanel import ModDetailPanel  # Import the isolated ModDetailPanel class

class ModDependencyListerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MC ZPatcher")
        self.selected_folder = None  # Store the folder path

        # Add menu bar
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Add "File" and "View" menu
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Open Mods Folder", command=self.select_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        view_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

        # Main section - mod list section and mod detail section side by side
        self.main_frame = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Mod List Section (left)
        self.mod_list_frame = tk.Frame(self.main_frame)
        self.tree = ttk.Treeview(self.mod_list_frame, columns=("Enabled", "Mod ID", "Mod Name", "Modloader", "Version"), show="headings")
        self.tree.heading("Enabled", text="Enabled")
        self.tree.heading("Mod ID", text="Mod ID")
        self.tree.heading("Mod Name", text="Mod Name")
        self.tree.heading("Modloader", text="Modloader")
        self.tree.heading("Version", text="Version")

        # Set default column widths
        self.tree.column("Enabled", width=65)

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Add scrollbars
        self.mod_list_scrollbar_y = Scrollbar(self.mod_list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.mod_list_scrollbar_y.set)
        self.mod_list_scrollbar_y.grid(row=0, column=1, sticky="ns")

        self.mod_list_scrollbar_x = Scrollbar(self.mod_list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.mod_list_scrollbar_x.set)
        self.mod_list_scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Allow dynamic resizing of the mod list
        self.mod_list_frame.grid_rowconfigure(0, weight=1)
        self.mod_list_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.add(self.mod_list_frame)

        # Separator for resizable layout (3 vertical dots)
        self.separator = ttk.Separator(self.main_frame, orient="vertical")
        self.main_frame.add(self.separator)

        # Create Mod Detail Panel (fix: use scroll_frame to add directly to PanedWindow)
        self.mod_detail_panel = ModDetailPanel(self.main_frame)
        self.main_frame.add(self.mod_detail_panel.scroll_frame)

        # Bind mod selection events (mouse release for selection)
        self.tree.bind("<ButtonRelease-1>", self.on_mod_select)

        # Bind checkboxes to click events (mouse press for checkbox)
        self.tree.bind("<Button-1>", self.on_checkbox_click)

        # Handle application closing to clean up
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def select_folder(self):
        # Get the folder path from file dialog
        folder_path = filedialog.askdirectory()
        self.selected_folder = folder_path

        if folder_path:
            # Clear the table before populating it with new data
            for row in self.tree.get_children():
                self.tree.delete(row)

            # Clear mod_temp_data folder if exists
            if os.path.exists("mod_temp_data"):
                shutil.rmtree("mod_temp_data")

            # Dynamically construct the path to the JAR file relative to the current Python script
            current_script_path = os.path.dirname(os.path.abspath(__file__))  # Path to the current Python script
            jar_path = os.path.join(current_script_path, '..', '..', '..', 'build', 'libs', 'MC-ZPatcher.jar')
            jar_path = os.path.abspath(jar_path)  # Convert to absolute path

            # Ensure the JAR file exists at the constructed path
            if not os.path.exists(jar_path):
                print(f"Error: JAR file not found at {jar_path}")
                return

            # Run the Java process with the dynamically determined JAR path
            try:
                # Capture stdout and stderr from the Java process and print it to the Python console
                result = subprocess.run(['java', '--enable-preview', '-jar', jar_path, folder_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                # Print the output from the Java process
                print(result.stdout)  # Print standard output (includes our custom messages)
                print(result.stderr)  # Print any error output

                if result.returncode != 0:
                    print(f"Error running Java process: {result.stderr}")
                    return

                # Load the extracted mod data from JSON
                self.load_mod_data("mod_temp_data/mod_data.json")

            except Exception as e:
                print(f"Error accessing JAR file: {e}")

    def load_mod_data(self, json_file):
        """Load the JSON data and populate the mod list with the correct fields."""
        try:
            with open(json_file, 'r') as f:
                self.mod_info = json.load(f)  # Store all mod data in a class attribute

            # Populate the table with mod info
            for mod in self.mod_info:
                # Retrieve data from the mod JSON
                enabled = "☑" if mod.get("enabled", True) else "☐"
                mod_id = mod.get("id", "Unknown")  # "id" is the correct key for Mod ID
                mod_name = mod.get("name", mod_id)  # If no mod name, fallback to mod ID
                modloader = mod.get("modloader", "Unknown")  # For now, modloader is "Unknown"
                version = mod.get("version", "Unknown")  # "version" key is correct

                # Insert mod data into the Treeview
                self.tree.insert("", "end", values=(enabled, mod_id, mod_name, modloader, version))

        except FileNotFoundError:
            print(f"File {json_file} not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")

    def on_mod_select(self, event):
        """Handles mod selection to display details when a mod is selected"""
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item, "values")
        mod_id = values[1]  # Correct mod ID extraction

        # Find the mod details in the loaded JSON data
        selected_mod_data = next((mod for mod in self.mod_info if mod.get('id') == mod_id), None)
        if selected_mod_data:
            # Update the mod detail panel with the correct mod data
            self.mod_detail_panel.update_mod_details(selected_mod_data)

    def on_checkbox_click(self, event):
        """Handles checkbox clicks for enabling/disabling mods"""
        region = self.tree.identify("region", event.x, event.y)
        column = self.tree.identify_column(event.x)

        if region == "cell" and column == "#1":  # Only react to clicks in the checkbox column
            item = self.tree.identify_row(event.y)
            if item:
                self.toggle_mod(item)

    def toggle_mod(self, item):
        # Fetch current values from the selected mod row
        values = self.tree.item(item, "values")
        mod_id = values[1]
        selected_mod_data = next((mod for mod in self.mod_info if mod.get('mod_id') == mod_id), None)

        if selected_mod_data:
            mod_file = selected_mod_data.get('file_path')  # Get the stored file path
            enabled = selected_mod_data.get('enabled')  # Check if currently enabled

            if mod_file:
                try:
                    # Rename the file to enable or disable the mod
                    if enabled:
                        new_mod_file = mod_file + ".disabled"
                        os.rename(mod_file, new_mod_file)
                        self.tree.set(item, "Enabled", "☐")  # Update checkbox status
                    else:
                        new_mod_file = mod_file.replace(".disabled", "")
                        os.rename(mod_file, new_mod_file)
                        self.tree.set(item, "Enabled", "☑")

                    # Ensure mod paths and details are updated
                    self.update_mod_path(mod_id, new_mod_file)

                except Exception as e:
                    print(f"Error renaming mod file: {e}")

    def update_mod_path(self, mod_id, new_mod_file):
        """Update the mod path in the loaded mod info after renaming the file"""
        selected_mod_data = next((mod for mod in self.mod_info if mod.get('mod_id') == mod_id), None)
        if selected_mod_data:
            selected_mod_data['file_path'] = new_mod_file
            selected_mod_data['enabled'] = not new_mod_file.endswith(".disabled")
            self.on_mod_select(None)  # Refresh the details panel

    def on_exit(self):
        """Handle application exit by cleaning up the mod_temp_data folder"""
        if os.path.exists("mod_temp_data"):
            shutil.rmtree("mod_temp_data")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModDependencyListerApp(root)
    root.geometry("1200x800")
    root.mainloop()
