# VersionControlPanel.py
import tkinter as tk
from tkinter import ttk

class VersionControlPanel:
    """Handles the display and updating of version control details."""

    def __init__(self, parent, curseforge_query_callback):
        self.parent = parent
        self.curseforge_query_callback = curseforge_query_callback

        # Scrollable area setup
        self.scroll_frame = tk.Frame(self.parent)
        self.canvas = tk.Canvas(self.scroll_frame, bg="white")
        self.scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_content = ttk.Frame(self.canvas)
        self.scroll_content.bind("<Configure>", self.on_resize)

        self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Add Minecraft version dropdown
        self.create_minecraft_version_dropdown()

        # Add Loader dropdown with full modloader list
        self.create_loader_dropdown()

        # Add mod status labels
        self.create_mod_status_labels()

        # Add CurseForge and ModRinth sync labels
        self.create_sync_labels()

        # Add Find on CurseForge button
        self.create_find_on_curseforge_button()

    def create_minecraft_version_dropdown(self):
        """Creates a dropdown menu for selecting a Minecraft version."""
        versions = ["1.21.3", "1.21.2", "1.21.1", "1.21", ... ]  # Full version list as before

        label = tk.Label(self.scroll_content, text="Minecraft Version:", bg="white", font=("Arial", 10, "bold"))
        label.pack(pady=5)

        self.version_var = tk.StringVar(self.scroll_content)
        self.version_var.set("Select a version")  # Default display text

        version_dropdown = ttk.Combobox(
            self.scroll_content, textvariable=self.version_var, values=versions, state="readonly"
        )
        version_dropdown.pack(pady=5, fill="x")

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

        label = tk.Label(self.scroll_content, text="Loader:", bg="white", font=("Arial", 10, "bold"))
        label.pack(pady=5)

        self.loader_var = tk.StringVar(self.scroll_content)
        self.loader_var.set("Select a loader")  # Default display text

        # Store loader types in a dictionary for easy access
        self.loader_dict = {name: value for name, value in loaders}
        loader_dropdown = ttk.Combobox(
            self.scroll_content, textvariable=self.loader_var, values=[name for name, _ in loaders], state="readonly"
        )
        loader_dropdown.pack(pady=5, fill="x")

    def create_mod_status_labels(self):
        """Creates labels to show the number of up-to-date and outdated mods."""
        self.up_to_date_label = tk.Label(self.scroll_content, text="Up-to-date mods: 0", bg="white", font=("Arial", 10))
        self.up_to_date_label.pack(pady=(10, 2))

        self.outdated_label = tk.Label(self.scroll_content, text="Outdated mods: 0", bg="white", font=("Arial", 10))
        self.outdated_label.pack(pady=2)

        self.mods_found_label = tk.Label(self.scroll_content, text="Mods found: 0", bg="white", font=("Arial", 10))
        self.mods_found_label.pack(pady=2)

    def create_sync_labels(self):
        """Creates labels to show sync status with CurseForge and ModRinth."""
        self.curseforge_sync_label = tk.Label(self.scroll_content, text="CurseForge sync: 0", bg="white", font=("Arial", 10))
        self.curseforge_sync_label.pack(pady=2)

        self.modrinth_sync_label = tk.Label(self.scroll_content, text="ModRinth sync: 0", bg="white", font=("Arial", 10))
        self.modrinth_sync_label.pack(pady=2)

    def create_find_on_curseforge_button(self):
        """Creates a button to query CurseForge for all mods in the list."""
        self.find_curseforge_button = tk.Button(
            self.scroll_content, text="Find on CurseForge", state="disabled",
            font=("Arial", 10, "bold"), command=self.curseforge_query_callback
        )
        self.find_curseforge_button.pack(pady=(15, 10), fill="x")

    def on_resize(self, event):
        """Adjust scroll region to the contents' bounding box."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_frame(self):
        """Returns the frame that contains the version control panel."""
        return self.scroll_frame

    def update_find_button_state(self, state):
        """Enable or disable the Find on CurseForge button."""
        self.find_curseforge_button.config(state=state)

    def update_mod_counts(self, mods_found, up_to_date, outdated, curseforge_sync, modrinth_sync):
        """Updates the mod-related label counts."""
        self.mods_found_label.config(text=f"Mods found: {mods_found}")
        self.up_to_date_label.config(text=f"Up-to-date mods: {up_to_date}")
        self.outdated_label.config(text=f"Outdated mods: {outdated}")
        self.curseforge_sync_label.config(text=f"CurseForge sync: {curseforge_sync}")
        self.modrinth_sync_label.config(text=f"ModRinth sync: {modrinth_sync}")

    def get_selected_loader_type(self):
        """Returns the selected loader type as an integer for the CurseForge API."""
        return self.loader_dict.get(self.loader_var.get(), 0)  # Default to 0 (Any)

