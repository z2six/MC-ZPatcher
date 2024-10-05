import tkinter as tk
from tkinter import filedialog, Menu
import shutil
import subprocess
from ModDetailPanel import ModDetailPanel
from ModListPanel import ModListPanel
from ConfigHandler import ConfigHandler
import json
import os

class ModDependencyListerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MC ZPatcher")
        self.selected_folder = None  # Store the folder path

        # Load or create config
        self.config_handler = ConfigHandler()  # Initialize config handler
        self.config = self.config_handler.load_or_create_config()  # Load the config

        # Add menu bar
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Add "File" menu
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Open Mods Folder", command=self.select_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Add "View" menu
        view_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

        # Add "Panels" submenu
        panels_menu = Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Panels", menu=panels_menu)

        # List Panel Submenu (Columns)
        list_panel_menu = Menu(panels_menu, tearoff=0)
        list_panel_menu.add_command(label="Columns", command=self.on_columns_click)
        panels_menu.add_cascade(label="List Panel", menu=list_panel_menu)

        # Detail Panel Submenu
        detail_panel_menu = Menu(panels_menu, tearoff=0)
        self.detail_panel_enabled_var = tk.BooleanVar(value=self.config['detailpane']['enabled'])
        detail_panel_menu.add_checkbutton(label="Enabled", variable=self.detail_panel_enabled_var, command=self.toggle_detail_panel)
        self.detail_panel_popout_var = tk.BooleanVar(value=self.config['detailpane']['popout'])
        detail_panel_menu.add_checkbutton(label="Popout", variable=self.detail_panel_popout_var, command=self.toggle_detail_popout)
        panels_menu.add_cascade(label="Detail Panel", menu=detail_panel_menu)

        # Version Control Panel Submenu
        version_panel_menu = Menu(panels_menu, tearoff=0)
        self.version_panel_enabled_var = tk.BooleanVar(value=self.config['versionpane']['enabled'])
        version_panel_menu.add_checkbutton(label="Enabled", variable=self.version_panel_enabled_var, command=self.toggle_version_panel)
        self.version_panel_popout_var = tk.BooleanVar(value=self.config['versionpane']['popout'])
        version_panel_menu.add_checkbutton(label="Popout", variable=self.version_panel_popout_var, command=self.toggle_version_popout)
        panels_menu.add_cascade(label="Version Control Panel", menu=version_panel_menu)

        # Main layout with mod list and mod detail sections
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Mod List Section (left)
        self.mod_list_frame = tk.Frame(self.main_frame, width=600, height=800)
        self.mod_list_frame.grid(row=0, column=0, sticky="nswe")
        self.mod_list_panel = ModListPanel(self.mod_list_frame, self.on_mod_select, self.on_checkbox_click)
        self.mod_list_panel.get_frame().pack(fill="both", expand=True)

        # Add a 1px vertical grey divider (now draggable)
        self.divider = tk.Frame(self.main_frame, width=1, bg="grey", cursor="sb_h_double_arrow")
        self.divider.grid(row=0, column=1, sticky="ns")
        self.divider.bind("<Button-1>", self.start_drag)
        self.divider.bind("<B1-Motion>", self.do_drag)

        # Create Mod Detail Panel (conditionally based on config)
        self.mod_detail_panel = None
        self.mod_detail_frame = tk.Frame(self.main_frame, width=400, height=800)
        if self.config['detailpane']['enabled']:
            self.mod_detail_panel = ModDetailPanel(self.mod_detail_frame)
            self.mod_detail_panel.scroll_frame.pack(fill="both", expand=True)
        self.mod_detail_frame.grid(row=0, column=2, sticky="nswe")

        # Ensure mod_list_frame allows dynamic resizing
        self.main_frame.grid_columnconfigure(0, weight=1)  # Only the Mod List should resize
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Store the starting position for dragging the divider
        self.start_x = 0
        self.start_list_weight = 0
        self.start_detail_weight = 0

        # Handle application closing to clean up
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def start_drag(self, event):
        """Record the starting position for the divider drag."""
        self.start_x = event.x
        self.start_list_weight = self.main_frame.grid_columnconfigure(0)['weight']
        self.start_detail_weight = self.main_frame.grid_columnconfigure(2)['weight']

    def do_drag(self, event):
        """Handle the dragging of the divider and resize the panels."""
        delta_x = event.x - self.start_x
        total_width = self.main_frame.winfo_width()

        # Calculate the percentage of the drag relative to the total window width
        list_weight_delta = (delta_x / total_width) * 5  # Arbitrary scale factor for sensitivity
        detail_weight_delta = -list_weight_delta

        new_list_weight = max(1, int(self.start_list_weight + list_weight_delta))
        new_detail_weight = max(1, int(self.start_detail_weight + detail_weight_delta))

        # Set the new column weights based on drag
        self.main_frame.grid_columnconfigure(0, weight=new_list_weight)
        self.main_frame.grid_columnconfigure(2, weight=new_detail_weight)
        self.main_frame.update_idletasks()  # Force the layout to refresh

    def toggle_detail_panel(self):
        """Toggles the visibility of the detail panel based on the menu selection."""
        enabled = self.detail_panel_enabled_var.get()
        self.config['detailpane']['enabled'] = enabled
        self.config_handler.save_config(self.config)

        if enabled:
            # Add the ModDetailPanel if it doesn't already exist
            if not self.mod_detail_panel:
                self.mod_detail_panel = ModDetailPanel(self.mod_detail_frame)
                self.mod_detail_panel.scroll_frame.pack(fill="both", expand=True)
            self.mod_detail_frame.grid()  # Make the frame visible

            # Update grid column weights when the detail panel is shown
            self.main_frame.grid_columnconfigure(0, weight=3)
            self.main_frame.grid_columnconfigure(2, weight=2)

            # If a mod is selected, update the ModDetailPanel with mod details
            selected_items = self.mod_list_panel.tree.selection()
            if selected_items:
                selected_item = selected_items[0]
                values = self.mod_list_panel.tree.item(selected_item, "values")
                mod_id = values[1]
                selected_mod_data = next((mod for mod in self.mod_list_panel.mod_info if mod.get('id') == mod_id), None)
                if selected_mod_data:
                    self.mod_detail_panel.update_mod_details(selected_mod_data)

        else:
            # Remove the ModDetailPanel from the frame
            if self.mod_detail_panel:
                self.mod_detail_frame.grid_remove()  # Hide the frame
                self.mod_detail_panel = None

            # Expand the Mod List to full width when detail panel is hidden
            self.main_frame.grid_columnconfigure(0, weight=1)  # Mod List takes full width
            self.main_frame.grid_columnconfigure(2, weight=0)  # Detail panel has no weight

    def toggle_detail_popout(self):
        """Toggles the popout setting of the detail panel."""
        self.config['detailpane']['popout'] = self.detail_panel_popout_var.get()
        self.config_handler.save_config(self.config)

    def toggle_version_panel(self):
        """Handles toggling the version control panel (similar to toggle_detail_panel)."""
        pass

    def toggle_version_popout(self):
        """Toggles the popout setting of the version control panel."""
        self.config['versionpane']['popout'] = self.version_panel_popout_var.get()
        self.config_handler.save_config(self.config)

    def on_columns_click(self):
        """Opens the column settings for the list panel."""
        pass

    def select_folder(self):
        # Get the folder path from file dialog
        folder_path = filedialog.askdirectory()
        self.selected_folder = folder_path

        if folder_path:
            if os.path.exists("mod_temp_data"):
                shutil.rmtree("mod_temp_data")
            jar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'build', 'libs', 'MC-ZPatcher.jar')

            if not os.path.exists(jar_path):
                print(f"Error: JAR file not found at {jar_path}")
                return

            try:
                result = subprocess.run(['java', '--enable-preview', '-jar', jar_path, folder_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                print(result.stdout, result.stderr)

                if result.returncode != 0:
                    print(f"Error running Java process: {result.stderr}")
                    return

                self.load_mod_data("mod_temp_data/mod_data.json")

            except Exception as e:
                print(f"Error accessing JAR file: {e}")

    def load_mod_data(self, json_file):
        """Load the JSON data and populate the mod list with the correct fields."""
        try:
            with open(json_file, 'r') as f:
                mod_data = json.load(f)
            self.mod_list_panel.populate_mod_list(mod_data)
        except FileNotFoundError:
            print(f"File {json_file} not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")

    def on_mod_select(self, event):
        """Handles mod selection to display details when a mod is selected."""
        selected_items = self.mod_list_panel.tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            values = self.mod_list_panel.tree.item(selected_item, "values")
            mod_id = values[1]
            selected_mod_data = next((mod for mod in self.mod_list_panel.mod_info if mod.get('id') == mod_id), None)
            if selected_mod_data and self.mod_detail_panel:
                self.mod_detail_panel.update_mod_details(selected_mod_data)

    def on_checkbox_click(self, event):
        """Handles checkbox clicks for enabling/disabling mods."""
        region = self.mod_list_panel.tree.identify("region", event.x, event.y)
        column = self.mod_list_panel.tree.identify_column(event.x)

        if region == "cell" and column == "#1":
            item = self.mod_list_panel.tree.identify_row(event.y)
            if item:
                self.mod_list_panel.toggle_mod(item)

    def on_exit(self):
        """Handle application exit by cleaning up the mod_temp_data folder."""
        if os.path.exists("mod_temp_data"):
            shutil.rmtree("mod_temp_data")
        self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = ModDependencyListerApp(root)
    root.geometry("1200x800")
    root.mainloop()
