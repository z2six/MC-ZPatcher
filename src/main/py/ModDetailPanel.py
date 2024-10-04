import tkinter as tk
from PIL import Image, ImageTk
import os

class ModDetailPanel:
    """Handles the display and updating of the mod details."""
    def __init__(self, parent):
        self.parent = parent

        # Create the mod details frame
        self.mod_detail_frame = tk.Frame(self.parent, relief="sunken", borderwidth=2, width=350)

        # Configure row and column weights to prevent excessive space allocation
        self.mod_detail_frame.grid_rowconfigure(0, weight=0)  # No extra space for the icon row
        self.mod_detail_frame.grid_rowconfigure(1, weight=0)  # For the general section
        self.mod_detail_frame.grid_rowconfigure(2, weight=0)  # For the mod ID
        self.mod_detail_frame.grid_columnconfigure(0, weight=1)  # Allow the column to expand

        # Mod detail widgets
        self.icon_label = tk.Label(self.mod_detail_frame)
        self.icon_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="n")  # Minimal padding at the bottom

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
            icon_image = Image.open(icon_path).resize((128, 128))  # Ensure 128x128 size
            icon_tk = ImageTk.PhotoImage(icon_image)
            self.icon_label.config(image=icon_tk)
            self.icon_label.image = icon_tk  # Keep reference to prevent garbage collection
        else:
            self.display_placeholder_icon()

    def display_placeholder_icon(self):
        """Displays a green placeholder box if no icon is found."""
        green_box = Image.new("RGB", (128, 128), color="green")
        green_tk = ImageTk.PhotoImage(green_box)
        self.icon_label.config(image=green_tk)
        self.icon_label.image = green_tk
