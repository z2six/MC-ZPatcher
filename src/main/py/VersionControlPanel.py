from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QScrollArea
)
import threading
import os
import json
import requests
from CurseForgeAPI import CurseForgeSync

class VersionControlPanel(QWidget):
    """Handles the display and updating of version control details, including syncing with CurseForge."""

    def __init__(self, parent=None, curseforge_query_callback=None, mod_list_panel=None):
        super().__init__(parent)
        self.mod_list_panel = mod_list_panel  # Store the direct reference to ModListPanel
        self.curseforge_sync = CurseForgeSync(api_key="$2a$10$U0nSm8OTYzwQQ2IYf6ohzO0h5rPMAQIgudlFWzT.omWZoWHj1BloG")
        self.curseforge_query_callback = curseforge_query_callback

        # Set up the main layout and scroll area
        self.layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # Add dropdowns, labels, and button
        self.create_minecraft_version_dropdown()
        self.create_loader_dropdown()
        self.create_mod_status_labels()
        self.create_sync_labels()
        self.create_find_on_curseforge_button()

    def create_minecraft_version_dropdown(self):
        """Creates a dropdown menu for selecting a Minecraft version."""
        versions = ["1.21.3", "1.21.2", "1.21.1", "1.21"]

        label = QLabel("Minecraft Version:")
        label.setStyleSheet("font-weight: bold;")
        self.scroll_layout.addWidget(label)

        self.version_dropdown = QComboBox(self.scroll_content)
        self.version_dropdown.addItems(["Select a version"] + versions)
        self.scroll_layout.addWidget(self.version_dropdown)

    def create_loader_dropdown(self):
        """Creates a dropdown menu for selecting a loader type with CurseForge enums."""
        loaders = [
            ("Forge", 1),
            ("Cauldron", 2),
            ("LiteLoader", 3),
            ("Fabric", 4),
            ("Quilt", 5),
            ("NeoForge", 6)
        ]

        label = QLabel("Loader:")
        label.setStyleSheet("font-weight: bold;")
        self.scroll_layout.addWidget(label)

        self.loader_dropdown = QComboBox(self.scroll_content)
        self.loader_dropdown.addItem("Select a loader")
        for name, _ in loaders:
            self.loader_dropdown.addItem(name)

        # Store loader types in a dictionary for easy access
        self.loader_dict = {name: value for name, value in loaders}
        self.scroll_layout.addWidget(self.loader_dropdown)

    def create_mod_status_labels(self):
        """Creates labels to show the number of up-to-date and outdated mods."""
        self.up_to_date_label = QLabel("Up-to-date mods: 0")
        self.outdated_label = QLabel("Outdated mods: 0")
        self.mods_found_label = QLabel("Mods found: 0")

        for label in (self.up_to_date_label, self.outdated_label, self.mods_found_label):
            label.setStyleSheet("font-size: 10pt;")
            self.scroll_layout.addWidget(label)

    def create_sync_labels(self):
        """Creates labels to show sync status with CurseForge and ModRinth."""
        self.curseforge_sync_label = QLabel("CurseForge sync: 0")
        self.modrinth_sync_label = QLabel("ModRinth sync: 0")

        for label in (self.curseforge_sync_label, self.modrinth_sync_label):
            label.setStyleSheet("font-size: 10pt;")
            self.scroll_layout.addWidget(label)

    def create_find_on_curseforge_button(self):
        """Creates a button to query CurseForge for all mods in the list."""
        self.find_curseforge_button = QPushButton("Find on CurseForge")
        self.find_curseforge_button.setEnabled(False)
        self.find_curseforge_button.setStyleSheet("font-weight: bold; font-size: 10pt;")
        self.find_curseforge_button.clicked.connect(self.initiate_curseforge_sync)
        self.scroll_layout.addWidget(self.find_curseforge_button)

    def update_find_button_state(self, state):
        """Enable or disable the Find on CurseForge button."""
        self.find_curseforge_button.setEnabled(state == "normal")

    def update_mod_counts(self, mods_found, up_to_date, outdated, curseforge_sync, modrinth_sync):
        """Updates the mod-related label counts."""
        self.mods_found_label.setText(f"Mods found: {mods_found}")
        self.up_to_date_label.setText(f"Up-to-date mods: {up_to_date}")
        self.outdated_label.setText(f"Outdated mods: {outdated}")
        self.curseforge_sync_label.setText(f"CurseForge sync: {curseforge_sync}")
        self.modrinth_sync_label.setText(f"ModRinth sync: {modrinth_sync}")

    def get_selected_loader_type(self):
        """Returns the selected loader type as an integer for the CurseForge API."""
        selected_loader = self.loader_dropdown.currentText()
        return self.loader_dict.get(selected_loader, 0)  # Default to 0 (Any)

    def initiate_curseforge_sync(self):
        """Launch the CurseForge sync in a separate thread to avoid freezing the GUI."""
        mod_list = self.mod_list_panel.mod_info  # Direct access to mod_info from ModListPanel

        # Debugging lines
        print("Initiate CurseForge Sync - mod_list contents:", mod_list)
        print("Type of mod_list:", type(mod_list))

        if not isinstance(mod_list, list):
            print("Error: mod_list is not a list, cannot proceed with CurseForge sync.")
            return

        threading.Thread(target=self._find_on_curseforge_background, args=(mod_list,), daemon=True).start()

    def _find_on_curseforge_background(self, mod_list):
        """Background thread function to query CurseForge for each mod in the list."""
        for mod in mod_list:
            unique_id = mod.get("unique_id")
            self.mod_list_panel.update_cf_sync_status(unique_id, "searching")  # Set searching icon
            self.search_mod_on_curseforge(mod)  # Calls search_mod_on_curseforge, which applies strip_disabled_suffix

        # Update icon after search completes, based on result
            if mod.get("curseforge_project_id"):
                self.mod_list_panel.update_cf_sync_status(unique_id, "found")
            else:
                self.mod_list_panel.update_cf_sync_status(unique_id, "not_found")

    def search_mod_on_curseforge(self, mod):
        """Handles the actual CurseForge search, updates CF Sync status, and saves relevant data."""
        unique_id = mod.get("unique_id")

        # Set the CF Sync icon to "searching" by emitting the signal
        self.mod_list_panel.update_icon_signal.emit(unique_id, "searching")

        file_path = mod.get("file_path")
        mod_name = mod.get("name")

        # Use the utility function to strip '.disabled' suffix for lookup
        clean_file_path = self.strip_disabled_suffix(file_path)
        print(f"[DEBUG] Searching with clean file path: {clean_file_path}")

        found_mod = None
        if clean_file_path and os.path.isfile(file_path):
            found_mod = self.curseforge_sync.query_mod_by_hash(clean_file_path)
            if not found_mod:
                found_mod = self.curseforge_sync.query_mod_by_filename(mod_name, os.path.basename(clean_file_path))

        if found_mod:
            curseforge_project_id = found_mod.get("curseforge_id")
            slug = found_mod.get("curseforge_url", "").split('/')[-1]

            mod["curseforge_project_id"] = curseforge_project_id
            mod["curseforge_slug"] = slug

            print(f"[INFO] Retrieved CurseForge Project ID: {curseforge_project_id}")
            print(f"[INFO] Retrieved CurseForge Slug: {slug}")

            # Update JSON data with the project ID and slug
            self.update_mod_data_json(unique_id, "curseforge_project_id", curseforge_project_id)
            self.update_mod_data_json(unique_id, "curseforge_slug", slug)

            # Emit signal to set the CF Sync icon to "found"
            self.mod_list_panel.update_icon_signal.emit(unique_id, "found")
        else:
            # Emit signal to set the CF Sync icon to "not_found"
            self.mod_list_panel.update_icon_signal.emit(unique_id, "not_found")
            print(f"[INFO] No exact match found for filename: {os.path.basename(clean_file_path)} within mod results for: {mod_name}")

    def strip_disabled_suffix(self, filename):
        """Removes '.disabled' from filename if present for consistent querying."""
        return filename.replace('.jar.disabled', '.jar')

    def query_mod_slug_by_id(self, project_id):
        """Queries CurseForge API for the mod slug by project ID."""
        url = f"https://api.curseforge.com/v1/mods/{project_id}"
        headers = {"x-api-key": self.api_key}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            mod_data = response.json().get("data")
            if mod_data:
                return mod_data.get("slug")
        print(f"[ERROR] Failed to retrieve slug for project ID {project_id}")
        return None

    def update_mod_data_json(self, unique_id, field, value):
        """Updates a specific field in mod_data.json for the mod with the given unique_id."""
        json_path = os.path.join("mod_temp_data", "mod_data.json")

        try:
            with open(json_path, "r+") as f:
                data = json.load(f)
                for mod in data:
                    if mod.get("unique_id") == unique_id:
                        mod[field] = value
                        break
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error updating mod_data.json: {e}")

    def update_cf_sync_status(self, mod_id, status_key):
        """Updates the CF Sync status icon in the ModListPanel."""
        print(f"Updating CF Sync status for {mod_id} to {status_key}")
