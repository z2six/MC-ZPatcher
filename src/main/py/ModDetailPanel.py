import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import webbrowser


class ModDetailPanel:
    """Handles the display and updating of the mod details."""

    def __init__(self, parent):
        self.parent = parent
        self.sections = {}  # Dictionary to hold section details

        # Scrollable area setup
        self.scroll_frame = tk.Frame(self.parent)
        self.canvas = tk.Canvas(self.scroll_frame, bg="lightgray")
        self.scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_content = tk.Frame(self.canvas, bg="lightgray")
        self.scroll_content.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Create and position the icon label in the first row (centered horizontally)
        self.icon_label = tk.Label(self.scroll_content, bg="lightgray")
        self.icon_label.grid(row=0, column=0, padx=10, pady=(10, 0), columnspan=2)

        # Create the different sections with proper grid placement
        self.create_category_header("General", self.scroll_content, row=1, default_open=True)
        self.create_category_header("Compatibility", self.scroll_content, row=3, default_open=True)
        self.create_category_header("Contact", self.scroll_content, row=5, default_open=True)
        self.create_category_header("Technical", self.scroll_content, row=7, default_open=False)

        # Initialize fields for General, Compatibility, and Technical sections
        self.init_general_section()
        self.init_compatibility_section()
        self.init_technical_section()

    def create_category_header(self, title, parent_frame, row, default_open=True):
        """Creates an underlined category label with an arrow and toggle functionality."""
        header_frame = tk.Frame(parent_frame, bg="lightgray")
        header_frame.grid(row=row, column=0, sticky="nsew", pady=5, columnspan=2)

        # Arrow label that will point up or down depending on section state
        arrow_label = tk.Label(header_frame, text="▼" if default_open else "▲", font=("Arial", 12), bg="lightgray")
        arrow_label.grid(row=0, column=0, padx=5)

        # Category label (underlined)
        category_label = tk.Label(header_frame, text=title, font=("Arial", 12, "underline"), cursor="hand2", bg="lightgray")
        category_label.grid(row=0, column=1, sticky="w")

        # Create the section frame (content to show/hide)
        section_frame = tk.Frame(parent_frame, bg="lightgray")
        section_frame.grid(row=row + 1, column=0, sticky="nsew", padx=10, pady=5, columnspan=2)
        self.sections[title] = {'frame': section_frame, 'open': default_open, 'arrow': arrow_label, 'row': row + 1}

        # Initially show or hide the section based on the default state
        if not default_open:
            section_frame.grid_remove()

        # Bind the click event to toggle the section visibility
        category_label.bind("<Button-1>", lambda e: self.toggle_section(title))

    def toggle_section(self, section_name):
        """Toggles the visibility of a section and updates the arrow."""
        section = self.sections[section_name]
        if section['open']:
            section['frame'].grid_remove()
            section['arrow'].config(text="▲")
        else:
            section['frame'].grid(row=section['row'], column=0, sticky="nsew", columnspan=2)
            section['arrow'].config(text="▼")
        section['open'] = not section['open']
        self.update_scroll_region()

    def init_general_section(self):
        """Initializes the General section with empty fields (always visible)."""
        general_frame = self.sections['General']['frame']
        self.create_dedicated_block(general_frame, "Mod ID", "", 0)
        self.create_dedicated_block(general_frame, "Mod Name", "", 1)
        self.create_dedicated_block(general_frame, "Version", "", 2)
        self.create_dedicated_block(general_frame, "Description", "", 3)

    def init_compatibility_section(self):
        """Initializes the Compatibility section with empty fields (always visible)."""
        compatibility_frame = self.sections['Compatibility']['frame']
        self.create_dedicated_block(compatibility_frame, "Depends", {}, 0, list_mode=True)
        self.create_dedicated_block(compatibility_frame, "Recommends", {}, 1, list_mode=True)
        self.create_dedicated_block(compatibility_frame, "Breaks", {}, 2, list_mode=True)
        self.create_dedicated_block(compatibility_frame, "Conflicts", {}, 3, list_mode=True)

    def init_technical_section(self):
        """Initializes the Technical section with empty fields (always visible)."""
        technical_frame = self.sections['Technical']['frame']
        self.create_dedicated_block(technical_frame, "Environment", "", 0)
        self.create_dedicated_block(technical_frame, "Provides", {}, 1, list_mode=True)
        self.create_dedicated_block(technical_frame, "Suggests", {}, 2, list_mode=True)

    def update_mod_details(self, mod_data):
        """Updates the mod detail panel with the selected mod data."""
        # Clear previous labels to avoid overlapping data
        self.clear_section(self.sections['General']['frame'])
        self.clear_section(self.sections['Compatibility']['frame'])
        self.clear_section(self.sections['Contact']['frame'])
        self.clear_section(self.sections['Technical']['frame'])

        # Update the General section
        self.update_general_section(mod_data)

        # Update the Compatibility section
        self.update_compatibility_section(mod_data)

        # Update the Contact section (dynamically handle all available contact info)
        self.update_contact_section(mod_data.get("contact", {}))

        # Update the Technical section
        self.update_technical_section(mod_data)

        # Load and display the mod icon, if available
        self.update_icon(mod_data)

        self.update_scroll_region()

    def clear_section(self, frame):
        """Clears all widgets within a section frame to avoid old data mixing with new data."""
        for widget in frame.winfo_children():
            widget.destroy()

    def update_general_section(self, mod_data):
        """Updates the General section with mod ID, name, version, description."""
        general_frame = self.sections['General']['frame']
        self.create_dedicated_block(general_frame, "Mod ID", mod_data.get("id", "Unknown"), 0)
        self.create_dedicated_block(general_frame, "Mod Name", mod_data.get("name", "Unknown"), 1)
        self.create_dedicated_block(general_frame, "Version", mod_data.get("version", "Unknown"), 2)
        self.create_dedicated_block(general_frame, "Description", mod_data.get("description", "No description available"), 3)

    def update_compatibility_section(self, mod_data):
        """Updates the Compatibility section with depends, recommends, breaks, conflicts."""
        compatibility_frame = self.sections['Compatibility']['frame']
        self.create_dedicated_block(compatibility_frame, "Depends", mod_data.get("depends", {}), 0, list_mode=True)
        self.create_dedicated_block(compatibility_frame, "Recommends", mod_data.get("recommends", {}), 1, list_mode=True)
        self.create_dedicated_block(compatibility_frame, "Breaks", mod_data.get("breaks", {}), 2, list_mode=True)
        self.create_dedicated_block(compatibility_frame, "Conflicts", mod_data.get("conflicts", {}), 3, list_mode=True)

    def update_contact_section(self, contact_data):
        """Dynamically updates the Contact section with available contact fields."""
        contact_frame = self.sections['Contact']['frame']
        contact_fields = ['homepage', 'sources', 'issues', 'email', 'irc', 'discord']

        # Clear previous labels before dynamically updating
        self.clear_section(contact_frame)

        row = 0
        for field in contact_fields:
            if field in contact_data:
                self.create_clickable_label(contact_frame, field.capitalize(), contact_data[field], row)
                row += 2  # Add space for the next field (label and clickable link take 2 rows)

    def update_technical_section(self, mod_data):
        """Updates the Technical section with environment, provides, suggests."""
        technical_frame = self.sections['Technical']['frame']
        self.create_dedicated_block(technical_frame, "Environment", self.translate_environment(mod_data.get("environment", "*")), 0)
        self.create_dedicated_block(technical_frame, "Provides", mod_data.get("provides", {}), 1, list_mode=True)
        self.create_dedicated_block(technical_frame, "Suggests", mod_data.get("suggests", {}), 2, list_mode=True)

    def create_dedicated_block(self, frame, label_text, value, row, list_mode=False):
        """Creates a label and its corresponding data block (ensuring no overlap)."""
        # Label at the top
        label = tk.Label(frame, text=f"{label_text}:", anchor="w", justify="left", bg="lightgray", font=("Arial", 10, "bold"))
        label.grid(row=row, column=0, sticky="w", pady=2)

        # Value(s) below the label (handle both single value and list modes)
        if list_mode and isinstance(value, dict):
            # If value is a dictionary (for dependencies, etc.), display each item on a new line
            for i, (mod, version) in enumerate(value.items(), start=row + 1):
                value_label = tk.Label(frame, text=f"{mod} {version}", anchor="w", justify="left", bg="lightgray", wraplength=350)
                value_label.grid(row=i, column=0, sticky="w", padx=10)
        else:
            # Single line value
            value_label = tk.Label(frame, text=value, anchor="w", justify="left", bg="lightgray", wraplength=350)
            value_label.grid(row=row + 1, column=0, sticky="w", padx=10)

    def create_clickable_label(self, frame, field_name, url, row):
        """Creates a clickable label for URL fields in the Contact section."""
        label_text = f"{field_name}:"
        label = tk.Label(frame, text=label_text, anchor="w", justify="left", bg="lightgray", font=("Arial", 10, "bold"))
        label.grid(row=row, column=0, sticky="w", pady=2)

        # Show clickable URL on the next line
        url_label = tk.Label(frame, text=url, wraplength=350, justify="left", fg="blue", cursor="hand2", bg="lightgray")
        url_label.grid(row=row + 1, column=0, sticky="w", padx=10)

        # Make the URL clickable
        url_label.bind("<Button-1>", lambda e: webbrowser.open(url))

    def translate_environment(self, env_value):
        """Translates the environment field to more human-readable values."""
        if env_value == "*":
            return "Client and Server"
        elif env_value == "client":
            return "Client-Sided"
        elif env_value == "server":
            return "Server-Sided"
        return "Unknown"

    def update_icon(self, mod_data):
        """Loads the mod icon if available from the icon_path in JSON."""
        icon_path = mod_data.get('icon_path', None)
        if icon_path and os.path.exists(icon_path):
            icon_image = Image.open(icon_path).resize((128, 128))  # Ensure 128x128 size
            icon_tk = ImageTk.PhotoImage(icon_image)
            self.icon_label.config(image=icon_tk)
            self.icon_label.image = icon_tk  # Keep reference to prevent garbage collection
        else:
            self.display_placeholder_icon()

        # Ensure the icon is always centered horizontally
        self.icon_label.grid_configure(sticky="n")

    def display_placeholder_icon(self):
        """Displays a green placeholder box if no icon is found."""
        green_box = Image.new("RGB", (128, 128), color="green")
        green_tk = ImageTk.PhotoImage(green_box)
        self.icon_label.config(image=green_tk)
        self.icon_label.image = green_tk

    def update_scroll_region(self):
        """Updates the scroll region of the canvas dynamically."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

