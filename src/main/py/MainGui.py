# MainGui.py
import tkinter as tk
from PIL import Image, ImageTk  # Import ImageTk for handling PNG images
from tkinter import filedialog, Menu
import shutil
import subprocess
from ModDetailPanel import ModDetailPanel
from ModListPanel import ModListPanel
from VersionControlPanel import VersionControlPanel
from ConfigHandler import ConfigHandler
from ColumnSetting import ColumnSetting
from CurseForgeAPI import CurseForgeSync
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor

class ModDependencyListerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MC ZPatcher")
        self.selected_folder = None  # Store the folder path

        # Load or create config
        self.config_handler = ConfigHandler()
        self.config = self.config_handler.load_or_create_config()

        # Load icons for CF Sync status (assuming images are in `../resources/icons`)
        icon_folder = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons')
        self.icons = {
            "default": ImageTk.PhotoImage(Image.open(os.path.join(icon_folder, "orange_question.png")).resize((16, 16))),
            "searching": ImageTk.PhotoImage(Image.open(os.path.join(icon_folder, "blue_sync.png")).resize((16, 16))),
            "found": ImageTk.PhotoImage(Image.open(os.path.join(icon_folder, "green_checkmark.png")).resize((16, 16))),
            "not_found": ImageTk.PhotoImage(Image.open(os.path.join(icon_folder, "red_cross.png")).resize((16, 16))),
        }

        # Main layout with mod list and mod detail sections
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Version Control Panel setup
        self.version_control_frame = tk.Frame(self.main_frame, width=200, height=800)
        self.version_control_panel = VersionControlPanel(self.version_control_frame, self.find_on_curseforge)
        self.version_control_panel.get_frame().pack(fill="both", expand=True)

        # Check if Version Control Panel should be enabled from config
        if self.config['versionpane']['enabled']:
            self.version_control_frame.grid(row=0, column=0, sticky="nswe")

        # Define Mod List Frame first before initializing ModListPanel
        self.mod_list_frame = tk.Frame(self.main_frame, width=600, height=800)
        self.mod_list_frame.grid(row=0, column=1, sticky="nswe")

        # Initialize Mod List Panel, passing `self.icons`
        self.mod_list_panel = ModListPanel(self.mod_list_frame, self.on_mod_select, self.on_checkbox_click, icons=self.icons)
        self.mod_list_panel.get_frame().pack(fill="both", expand=True)

        # Initialize the ColumnSetting for column management
        self.column_setting = ColumnSetting(self.root, self.config_handler, self.config)

        # Add a 1px vertical grey divider (now draggable)
        self.divider = tk.Frame(self.main_frame, width=1, bg="grey", cursor="sb_h_double_arrow")
        self.divider.grid(row=0, column=2, sticky="ns")
        self.divider.bind("<Button-1>", self.start_drag)
        self.divider.bind("<B1-Motion>", self.do_drag)

        # Create Mod Detail Panel and show/hide based on config
        self.mod_detail_frame = tk.Frame(self.main_frame, width=400, height=800)
        self.mod_detail_panel = ModDetailPanel(self.mod_detail_frame)
        self.mod_detail_panel.scroll_frame.pack(fill="both", expand=True)

        # Check if Mod Detail Panel should be enabled from config
        if self.config['detailpane']['enabled']:
            self.mod_detail_frame.grid(row=0, column=3, sticky="nswe")

        # Ensure mod_list_frame allows dynamic resizing
        self.main_frame.grid_columnconfigure(1, weight=4)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Add menu bar
        self.menu_bar = Menu(self.root)
        self.root.config(menu=self.menu_bar)
        self.create_menu()

        # Store the starting position for dragging the divider
        self.start_x = 0
        self.start_list_weight = 0
        self.start_detail_weight = 0

        # Initialize CurseForgeSync with API key
        self.curseforge_sync = CurseForgeSync(api_key="$2a$10$U0nSm8OTYzwQQ2IYf6ohzO0h5rPMAQIgudlFWzT.omWZoWHj1BloG")

        # Handle application closing to clean up
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    def create_menu(self):
        # "File" menu
        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Open Mods Folder", command=self.select_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # "View" menu
        view_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

        # "Panels" submenu
        panels_menu = Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Panels", menu=panels_menu)

        # List Panel submenu
        list_panel_menu = Menu(panels_menu, tearoff=0)
        list_panel_menu.add_command(label="Columns", command=self.on_columns_click)
        panels_menu.add_cascade(label="List Panel", menu=list_panel_menu)

        # Detail Panel submenu
        detail_panel_menu = Menu(panels_menu, tearoff=0)
        self.detail_panel_enabled_var = tk.BooleanVar(value=self.config['detailpane']['enabled'])
        detail_panel_menu.add_checkbutton(label="Enabled", variable=self.detail_panel_enabled_var, command=self.toggle_detail_panel)
        self.detail_panel_popout_var = tk.BooleanVar(value=self.config['detailpane']['popout'])
        detail_panel_menu.add_checkbutton(label="Popout", variable=self.detail_panel_popout_var, command=self.toggle_detail_popout)
        panels_menu.add_cascade(label="Detail Panel", menu=detail_panel_menu)

        # Version Control Panel submenu
        version_panel_menu = Menu(panels_menu, tearoff=0)
        self.version_panel_enabled_var = tk.BooleanVar(value=self.config['versionpane']['enabled'])
        version_panel_menu.add_checkbutton(label="Enabled", variable=self.version_panel_enabled_var, command=self.toggle_version_panel)
        self.version_panel_popout_var = tk.BooleanVar(value=self.config['versionpane']['popout'])
        version_panel_menu.add_checkbutton(label="Popout", variable=self.version_panel_popout_var, command=self.toggle_version_popout)
        panels_menu.add_cascade(label="Version Control Panel", menu=version_panel_menu)

    def find_on_curseforge(self):
        """Launch the CurseForge search in a separate thread to avoid freezing the GUI."""
        threading.Thread(target=self._find_on_curseforge_background, daemon=True).start()

    def _find_on_curseforge_background(self):
        """Background thread function to query CurseForge for each mod in the list."""
        with ThreadPoolExecutor(max_workers=5) as executor:
            for mod in self.mod_list_panel.mod_info:
                mod_id = mod.get("id")
                # Update to searching icon before starting the background search
                self.root.after(0, self.mod_list_panel.update_cf_sync_status, mod_id, "searching")
                # Submit each mod's search as a separate task in the thread pool
                executor.submit(self.search_mod_on_curseforge, mod)

    def search_mod_on_curseforge(self, mod):
        """Handles the actual CurseForge search and updates CF Sync status."""
        file_path = mod.get("file_path")
        mod_name = mod.get("name")
        mod_id = mod.get("id")

        found_mod = None
        if file_path and os.path.isfile(file_path):
            # Try by hash first
            found_mod = self.curseforge_sync.query_mod_by_hash(file_path)

            # If not found by hash, fall back to filename
            if not found_mod:
                found_mod = self.curseforge_sync.query_mod_by_filename(mod_name, os.path.basename(file_path))

        # Schedule a GUI update to safely set the final CF Sync status
        final_status = "found" if found_mod else "not_found"
        self.root.after(0, self.mod_list_panel.update_cf_sync_status, mod_id, final_status)

    def start_drag(self, event):
        self.start_x = event.x
        self.start_list_weight = self.main_frame.grid_columnconfigure(1)['weight']
        self.start_detail_weight = self.main_frame.grid_columnconfigure(3)['weight']

    def do_drag(self, event):
        delta_x = event.x - self.start_x
        total_width = self.main_frame.winfo_width()

        list_weight_delta = (delta_x / total_width) * 5
        detail_weight_delta = -list_weight_delta

        new_list_weight = max(1, int(self.start_list_weight + list_weight_delta))
        new_detail_weight = max(1, int(self.start_detail_weight + detail_weight_delta))

        self.main_frame.grid_columnconfigure(1, weight=new_list_weight)
        self.main_frame.grid_columnconfigure(3, weight=new_detail_weight)
        self.main_frame.update_idletasks()

    def toggle_detail_panel(self):
        """Toggles the visibility of the detail panel based on the menu selection."""
        enabled = self.detail_panel_enabled_var.get()
        self.config['detailpane']['enabled'] = enabled
        self.config_handler.save_config(self.config)

        if enabled:
            self.mod_detail_frame.grid()
            selected_items = self.mod_list_panel.tree.selection()
            if selected_items:
                selected_item = selected_items[0]
                values = self.mod_list_panel.tree.item(selected_item, "values")
                mod_id = values[1]
                selected_mod_data = next((mod for mod in self.mod_list_panel.mod_info if mod.get('id') == mod_id), None)

                if selected_mod_data:
                    # Clear each section before updating details
                    self.mod_detail_panel.clear_section(self.mod_detail_panel.sections['General']['frame'])
                    self.mod_detail_panel.clear_section(self.mod_detail_panel.sections['Compatibility']['frame'])
                    self.mod_detail_panel.clear_section(self.mod_detail_panel.sections['Contact']['frame'])
                    self.mod_detail_panel.clear_section(self.mod_detail_panel.sections['Technical']['frame'])
                    self.mod_detail_panel.update_mod_details(selected_mod_data)

            self.main_frame.grid_columnconfigure(1, weight=4)
            self.main_frame.grid_columnconfigure(3, weight=2)
        else:
            self.mod_detail_frame.grid_remove()
            self.main_frame.grid_columnconfigure(1, weight=1)
            self.main_frame.grid_columnconfigure(3, weight=0)

    def toggle_detail_popout(self):
        self.config['detailpane']['popout'] = self.detail_panel_popout_var.get()
        self.config_handler.save_config(self.config)

    def toggle_version_panel(self):
        """Toggles the visibility of the version control panel based on the menu selection."""
        enabled = self.version_panel_enabled_var.get()
        self.config['versionpane']['enabled'] = enabled
        self.config_handler.save_config(self.config)

        if enabled:
            self.version_control_frame.grid(row=0, column=0, sticky="nswe")
            self.main_frame.grid_columnconfigure(0, weight=1)
        else:
            self.version_control_frame.grid_remove()
            self.main_frame.grid_columnconfigure(0, weight=0)

    def toggle_version_popout(self):
        self.config['versionpane']['popout'] = self.version_panel_popout_var.get()
        self.config_handler.save_config(self.config)

    def on_columns_click(self):
        self.column_setting.open_column_window()

    def enable_find_button(self):
        """Enable the 'Find on CurseForge' button once mods are loaded."""
        self.version_control_panel.update_find_button_state("normal")

    def select_folder(self):
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

                # Load mod data without querying CurseForge
                self.load_mod_data("mod_temp_data/mod_data.json")

                # Enable the Find on CurseForge button after loading mods
                self.enable_find_button()

            except Exception as e:
                print(f"Error accessing JAR file: {e}")

    def load_mod_data(self, json_file):
        """Loads mod data from a JSON file without querying CurseForge."""
        try:
            with open(json_file, 'r') as f:
                mod_data = json.load(f)

            # Populate mod list without querying CurseForge
            self.mod_list_panel.populate_mod_list(mod_data)

            # Update the Mods Found label
            mods_found_count = len(mod_data)
            self.version_control_panel.update_mod_counts(
                mods_found=mods_found_count,
                up_to_date=0,  # Placeholder
                outdated=0,    # Placeholder
                curseforge_sync=0,  # Sync will happen when button is clicked
                modrinth_sync=0  # Placeholder
            )

        except FileNotFoundError:
            print(f"File {json_file} not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON data: {e}")

    def update_mods_found(self, count):
        """Updates the Mods Found label dynamically."""
        self.mods_found_label.config(text=f"Mods found: {count}")

    def on_mod_select(self, event):
        """Handles mod selection to display details when a mod is selected."""
        selected_items = self.mod_list_panel.tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            values = self.mod_list_panel.tree.item(selected_item, "values")
            mod_id = values[1]
            selected_mod_data = next((mod for mod in self.mod_list_panel.mod_info if mod.get('id') == mod_id), None)
            if selected_mod_data:
                # Clear each section before updating details
                self.mod_detail_panel.clear_section(self.mod_detail_panel.sections['General']['frame'])
                self.mod_detail_panel.clear_section(self.mod_detail_panel.sections['Compatibility']['frame'])
                self.mod_detail_panel.clear_section(self.mod_detail_panel.sections['Contact']['frame'])
                self.mod_detail_panel.clear_section(self.mod_detail_panel.sections['Technical']['frame'])
                self.mod_detail_panel.update_mod_details(selected_mod_data)

    def on_checkbox_click(self, event):
        region = self.mod_list_panel.tree.identify("region", event.x, event.y)
        column = self.mod_list_panel.tree.identify_column(event.x)

        if region == "cell" and column == "#1":
            item = self.mod_list_panel.tree.identify_row(event.y)
            if item:
                self.mod_list_panel.toggle_mod(item)

    def on_exit(self):
        if os.path.exists("mod_temp_data"):
            shutil.rmtree("mod_temp_data")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModDependencyListerApp(root)
    root.geometry("1200x800")
    root.mainloop()
