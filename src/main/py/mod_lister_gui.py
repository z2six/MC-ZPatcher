import tkinter as tk
from tkinter import filedialog, ttk, Scrollbar
from PIL import Image, ImageTk
import os
import subprocess
import json

class ModDependencyListerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MC ZPatcher")
        self.selected_folder = None  # Store the folder path

        # Top section - full width, contains only the "Select Folder" button
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(fill="x", padx=10, pady=10)

        self.select_folder_btn = tk.Button(self.top_frame, text="Select Mod Folder", command=self.select_folder)
        self.select_folder_btn.pack()

        # Main section - mod list section and mod detail section side by side
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Mod List Section (left)
        self.mod_list_frame = tk.Frame(self.main_frame)
        self.mod_list_frame.grid(row=0, column=0, sticky="nsew")

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

        # Mod Detail Section (right)
        self.mod_detail_frame = tk.Frame(self.main_frame, relief="sunken", borderwidth=2, width=350)
        self.mod_detail_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Ensure mod details section has a fixed width of 350px (min and max)
        self.main_frame.grid_columnconfigure(1, minsize=350, weight=0)
        self.mod_detail_frame.grid_propagate(False)

        # Mod detail widgets
        self.icon_label = tk.Label(self.mod_detail_frame)
        self.icon_label.grid(row=0, column=0, rowspan=5, padx=10, pady=10)

        # General section
        self.separator_general = tk.Label(self.mod_detail_frame, text="----- General -----", fg="blue")
        self.separator_general.grid(row=6, column=0, sticky="w")

        self.mod_id_label = tk.Label(self.mod_detail_frame, text="Mod ID:", wraplength=350, justify="left")
        self.mod_id_label.grid(row=7, column=0, sticky="w")

        self.mod_name_label = tk.Label(self.mod_detail_frame, text="Mod Name:", wraplength=350, justify="left")
        self.mod_name_label.grid(row=8, column=0, sticky="w")

        self.mod_version_label = tk.Label(self.mod_detail_frame, text="Version:", wraplength=350, justify="left")
        self.mod_version_label.grid(row=9, column=0, sticky="w")

        self.description_label = tk.Label(self.mod_detail_frame, text="Description:", wraplength=350, justify="left")
        self.description_label.grid(row=10, column=0, sticky="w")

        # Compatibility section
        self.separator1 = tk.Label(self.mod_detail_frame, text="----- Compatibility -----", fg="blue")
        self.separator1.grid(row=11, column=0, sticky="w")

        self.compatibility_label = tk.Label(self.mod_detail_frame, text="Compatibility:", wraplength=350, justify="left")
        self.compatibility_label.grid(row=12, column=0, sticky="w")

        # Information section
        self.separator2 = tk.Label(self.mod_detail_frame, text="----- Information -----", fg="blue")
        self.separator2.grid(row=13, column=0, sticky="w")

        self.authors_label = tk.Label(self.mod_detail_frame, text="Authors:", wraplength=350, justify="left")
        self.authors_label.grid(row=14, column=0, sticky="w")

        self.contact_label = tk.Label(self.mod_detail_frame, text="Contact:", wraplength=350, justify="left")
        self.contact_label.grid(row=15, column=0, sticky="w")

        # Configure resizing behavior for mod list and mod details
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Bind mod selection events (mouse click and arrow keys)
        self.tree.bind("<ButtonRelease-1>", self.on_mod_select)
        self.tree.bind("<KeyRelease-Up>", self.on_mod_select)
        self.tree.bind("<KeyRelease-Down>", self.on_mod_select)

        # Bind checkboxes to click events
        self.tree.bind("<Double-1>", self.on_double_click)

    def select_folder(self):
        # Get the folder path from file dialog
        folder_path = filedialog.askdirectory()
        self.selected_folder = folder_path

        if folder_path:
            # Clear the table before populating it with new data
            for row in self.tree.get_children():
                self.tree.delete(row)

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
                result = subprocess.run(['java', '-jar', jar_path, folder_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

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
        # Load the JSON data file
        try:
            with open(json_file, 'r') as f:
                self.mod_info = json.load(f)  # Store all mod data in a class attribute

            # Populate the table with mod info
            for mod in self.mod_info:
                enabled = "☑" if mod.get("enabled", True) else "☐"
                mod_id = mod.get("mod_id", "Unknown")
                mod_name = mod.get("mod_name", "Unknown")
                modloader = mod.get("modloader", "Unknown")
                version = mod.get("version", "Unknown")

                # Insert mod data into the Treeview
                self.tree.insert("", "end", values=(enabled, mod_id, mod_name, modloader, version))

        except FileNotFoundError:
            print(f"File {json_file} not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")

    def on_mod_select(self, event):
        if not self.tree.selection():
            return  # Prevent errors if nothing is selected

        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item, "values")
        mod_id = values[1]

        # Find the mod details in the loaded JSON data
        selected_mod_data = next((mod for mod in self.mod_info if mod.get('mod_id') == mod_id), None)
        if selected_mod_data:
            # Update the detail panel with the mod information
            self.mod_id_label.config(text=f"Mod ID: {selected_mod_data.get('mod_id', 'Unknown')}")
            self.mod_name_label.config(text=f"Mod Name: {selected_mod_data.get('mod_name', 'Unknown')}")
            self.mod_version_label.config(text=f"Version: {selected_mod_data.get('version', 'Unknown')}")
            self.description_label.config(text=f"Description: {selected_mod_data.get('description', 'No description available')}")
            self.compatibility_label.config(text=f"Compatibility: {selected_mod_data.get('compatibility', 'Unknown')}")
            self.authors_label.config(text=f"Authors: {selected_mod_data.get('authors', 'Unknown')}")
            self.contact_label.config(text=f"Contact: {selected_mod_data.get('contact', 'Unknown')}")

            # Load the mod icon if available
            icon_path = f"mod_temp_data/icons/{mod_id}.png"
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path).resize((128, 128))
                icon_tk = ImageTk.PhotoImage(icon_image)
                self.icon_label.config(image=icon_tk)
                self.icon_label.image = icon_tk
            else:
                self.display_placeholder_icon()
        else:
            print(f"Mod ID {mod_id} not found in JSON data")

    def display_placeholder_icon(self):
        green_box = Image.new("RGB", (128, 128), color="green")
        green_tk = ImageTk.PhotoImage(green_box)
        self.icon_label.config(image=green_tk)
        self.icon_label.image = green_tk

    def on_double_click(self, event):
        # This handles toggling mod enable/disable when double-clicking the checkbox
        item = self.tree.selection()[0]
        self.toggle_mod(item)

    def toggle_mod(self, item):
        values = self.tree.item(item, "values")
        mod_id = values[1]
        enabled = values[0] == "☑"

        folder_path = self.selected_folder  # Use the globally stored selected folder path
        if folder_path:
            # Find the mod file and toggle between .jar and .jar.disabled
            mod_file = None
            for file in os.listdir(folder_path):
                if mod_id in file:
                    mod_file = os.path.join(folder_path, file)
                    break

            if mod_file:
                if enabled:
                    # Disable the mod by renaming to .jar.disabled
                    os.rename(mod_file, mod_file + ".disabled")
                    self.tree.set(item, "Enabled", "☐")
                else:
                    # Enable the mod by renaming to .jar
                    os.rename(mod_file, mod_file.replace(".disabled", ""))
                    self.tree.set(item, "Enabled", "☑")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModDependencyListerApp(root)
    root.geometry("1200x800")  # Wider window to accommodate mod details panel
    root.mainloop()
