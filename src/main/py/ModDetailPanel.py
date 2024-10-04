import tkinter as tk
from tkinter import filedialog, ttk, Scrollbar, Menu
from PIL import Image, ImageTk
import os
import subprocess
import json
import shutil

class ModDetailPanel:
    """Handles the display and updating of the mod details."""
    def __init__(self, parent):
        self.parent = parent

        # Create the mod details frame
        self.mod_detail_frame = tk.Frame(self.parent, relief="sunken", borderwidth=2, width=350)
        self.mod_detail_frame.grid_rowconfigure(0, weight=1)
        self.mod_detail_frame.grid_columnconfigure(0, weight=1)

        # Mod detail widgets
        self.icon_label = tk.Label(self.mod_detail_frame, pady=10)  # Reduced padding above and below icon to 10px
        self.icon_label.grid(row=0, column=0, rowspan=1, padx=10, pady=(10, 10))  # Control vertical padding here

        # General section
        self.separator_general = tk.Label(self.mod_detail_frame, text="----- General -----", fg="blue")
        self.separator_general.grid(row=1, column=0, sticky="w", pady=5)

        self.mod_id_label = tk.Label(self.mod_detail_frame, text="Mod ID:", wraplength=350, justify="left")
        self.mod_id_label.grid(row=2, column=0, sticky="w")

        self.mod_name_label = tk.Label(self.mod_detail_frame, text="Mod Name:", wraplength=350, justify="left")
        self.mod_name_label.grid(row=3, column=0, sticky="w")

        self.mod_version_label = tk.Label(self.mod_detail_frame, text="Version:", wraplength=350, justify="left")
        self.mod_version_label.grid(row=4, column=0, sticky="w")

        self.description_label = tk.Label(self.mod_detail_frame, text="Description:", wraplength=350, justify="left")
        self.description_label.grid(row=5, column=0, sticky="w")

        # Compatibility section
        self.separator1 = tk.Label(self.mod_detail_frame, text="----- Compatibility -----", fg="blue")
        self.separator1.grid(row=6, column=0, sticky="w", pady=5)

        self.compatibility_label = tk.Label(self.mod_detail_frame, text="Compatibility:", wraplength=350, justify="left")
        self.compatibility_label.grid(row=7, column=0, sticky="w")

        # Information section
        self.separator2 = tk.Label(self.mod_detail_frame, text="----- Information -----", fg="blue")
        self.separator2.grid(row=8, column=0, sticky="w", pady=5)

        # Word wrap for long text
        self.authors_label = tk.Label(self.mod_detail_frame, text="Authors:", wraplength=350, justify="left", anchor="w")
        self.authors_label.grid(row=9, column=0, sticky="w")

        self.contact_label = tk.Label(self.mod_detail_frame, text="Contact:", wraplength=350, justify="left", anchor="w")
        self.contact_label.grid(row=10, column=0, sticky="w")

    def update_mod_details(self, mod_data):
        """Updates the mod detail panel with the selected mod data."""
        self.mod_id_label.config(text=f"Mod ID: {mod_data.get('mod_id', 'Unknown')}")
        self.mod_name_label.config(text=f"Mod Name: {mod_data.get('mod_name', 'Unknown')}")
        self.mod_version_label.config(text=f"Version: {mod_data.get('version', 'Unknown')}")
        self.description_label.config(text=f"Description: {mod_data.get('description', 'No description available')}")
        self.compatibility_label.config(text=f"Compatibility: {mod_data.get('compatibility', 'Unknown')}")
        self.authors_label.config(text=f"Authors: {mod_data.get('authors', 'Unknown')}")
        self.contact_label.config(text=f"Contact: {mod_data.get('contact', 'Unknown')}")

        # Load the mod icon if available from the icon_path in JSON
        icon_path = mod_data.get('icon_path', None)
        if icon_path and os.path.exists(icon_path):
            icon_image = Image.open(icon_path).resize((128, 128))
            icon_tk = ImageTk.PhotoImage(icon_image)
            self.icon_label.config(image=icon_tk)
            self.icon_label.image = icon_tk
        else:
            self.display_placeholder_icon()

    def display_placeholder_icon(self):
        """Displays a green placeholder box if no icon is found."""
        green_box = Image.new("RGB", (128, 128), color="green")
        green_tk = ImageTk.PhotoImage(green_box)
        self.icon_label.config(image=green_tk)
        self.icon_label.image = green_tk


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

        self.mod_list_frame.grid_rowconfigure(0, weight=1)
        self.mod_list_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.add(self.mod_list_frame)

        # Separator for resizable layout
        self.separator = ttk.Separator(self.main_frame, orient="vertical")
        self.main_frame.add(self.separator)

        # Create Mod Detail Panel
        self.mod_detail_panel = ModDetailPanel(self.main_frame)
        self.main_frame.add(self.mod_detail_panel.mod_detail_frame)

        # Bind mod selection events (mouse release for selection)
        self.tree.bind("<ButtonRelease-1>", self.on_mod_select)

        # Bind checkboxes to click events (mouse press for checkbox)
        self.tree.bind("<Button-1>", self.on_checkbox_click)

        # Handle application closing to clean up
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def select_folder(self):
        """Existing logic for folder selection and data loading."""
        pass  # Omitted for brevity, keep as-is

    def load_mod_data(self, json_file):
        """Load mod data and update the mod list."""
        pass  # Omitted for brevity, keep as-is

    def on_mod_select(self, event):
        """Handles mod selection to display details when a mod is selected."""
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item, "values")
        mod_id = values[1]

        # Find the mod details in the loaded JSON data
        selected_mod_data = next((mod for mod in self.mod_info if mod.get('mod_id') == mod_id), None)
        if selected_mod_data:
            # Update the mod detail panel
            self.mod_detail_panel.update_mod_details(selected_mod_data)

    def on_checkbox_click(self, event):
        """Handles checkbox clicks for enabling/disabling mods."""
        pass  # Omitted for brevity, keep as-is

    def on_exit(self):
        """Handle application exit by cleaning up the mod_temp_data folder."""
        pass  # Omitted for brevity, keep as-is

if __name__ == "__main__":
    root = tk.Tk()
    app = ModDependencyListerApp(root)
    root.geometry("1200x800")
    root.mainloop()
