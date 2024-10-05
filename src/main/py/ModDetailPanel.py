# ModDetailPanel.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import webbrowser

class ModDetailPanel:
    """Handles the display and updating of the mod details."""

    def __init__(self, parent):
        self.parent = parent

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

        # Dictionary to hold sections (correct placement to avoid being reset)
        self.sections = {}

        # Create and position the icon label in the first row (centered horizontally)
        self.icon_label = tk.Label(self.scroll_content, bg="white")
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

        # Bind mouse scroll events to the canvas
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def create_category_header(self, title, parent_frame, row, default_open=True):
        """Creates an underlined category label with an arrow and toggle functionality."""
        header_frame = tk.Frame(parent_frame, bg="white")
        header_frame.grid(row=row, column=0, sticky="ew", pady=5, columnspan=2)

        # Arrow label that will point up or down depending on section state
        arrow_label = tk.Label(header_frame, text="▼" if default_open else "▲", font=("Arial", 12), bg="white")
        arrow_label.grid(row=0, column=0, padx=5)

        # Category label (underlined)
        category_label = tk.Label(header_frame, text=title, font=("Arial", 12, "underline"), cursor="hand2", bg="white")
        category_label.grid(row=0, column=1, sticky="w")

        # Create the section frame (content to show/hide)
        section_frame = tk.Frame(parent_frame, bg="white")
        section_frame.grid(row=row + 1, column=0, sticky="nsew", padx=10, pady=5, columnspan=2)
        section_frame.grid_columnconfigure(0, weight=1)  # Ensure the section frame stretches horizontally

        # Store in the sections dictionary
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

    def create_dedicated_block(self, frame, label_text, value, row, list_mode=False):
        """Creates a label and its corresponding data block (ensuring no overlap)."""
        label_frame = tk.Frame(frame)  # Each label has its own frame to handle dynamic width
        label_frame.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
        label_frame.grid_columnconfigure(0, weight=1)  # Ensure label frame stretches horizontally

        label = tk.Label(label_frame, text=f"{label_text}:", anchor="w", wraplength=self.get_wraplength())  # Wraplength for label
        label.pack(side="left", anchor="w")

        if list_mode and isinstance(value, dict):
            for i, (mod, version) in enumerate(value.items(), start=row + 1):
                value_label = tk.Label(label_frame, text=f"{mod} {version}", anchor="w", wraplength=self.get_wraplength())
                value_label.pack(anchor="w", padx=10)
        else:
            value_label = tk.Label(label_frame, text=value, anchor="w", wraplength=self.get_wraplength())  # Wraplength for value
            value_label.pack(anchor="w", padx=10)

    def update_scroll_region(self):
        """Ensures the scrollable area is properly sized after updates."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mouse_wheel(self, event):
        """Handles mouse wheel scrolling."""
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def on_middle_click_scroll(self, event):
        """Start the middle mouse button scroll."""
        self.canvas.scan_mark(event.x, event.y)

    def on_middle_drag_scroll(self, event):
        """Handles middle mouse button dragging to scroll."""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_resize(self, event):
        """Handles both scroll region update and dynamic word wrapping on resize."""
        self.update_scroll_region()
        self.update_wraplength(event)

    def get_wraplength(self):
        """Returns a suitable wraplength based on the current width of the parent canvas."""
        return max(self.canvas.winfo_width() - 20, 100)  # Ensure padding around the edges

    def update_wraplength(self, event):
        """Updates the wraplength of all labels when the panel is resized."""
        new_wraplength = self.get_wraplength()
        for widget in self.scroll_content.winfo_children():
            if isinstance(widget, tk.Label):  # Apply wraplength to tk.Labels
                widget.config(wraplength=new_wraplength)

    def update_icon(self, mod_data):
        """Loads and displays the mod icon."""
        icon_path = mod_data.get("icon_path")
        if icon_path and os.path.exists(icon_path):
            try:
                icon_img = Image.open(icon_path)
                icon_img = icon_img.resize((64, 64), Image.Resampling.LANCZOS)
                icon_photo = ImageTk.PhotoImage(icon_img)
                self.icon_label.config(image=icon_photo)
                self.icon_label.image = icon_photo  # Keep a reference to avoid garbage collection
            except Exception as e:
                print(f"Error loading icon: {e}")

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

    def create_clickable_label(self, frame, label_text, url, row):
        """Creates a clickable link label for the provided URL."""
        # Label for the field name
        label = tk.Label(frame, text=f"{label_text}:", anchor="w", justify="left", bg="white", font=("Arial", 10, "bold"))
        label.grid(row=row, column=0, sticky="w", pady=2)

        # Clickable link label
        link_label = tk.Label(frame, text=url, anchor="w", justify="left", fg="blue", cursor="hand2", bg="white", wraplength=self.get_wraplength())
        link_label.grid(row=row + 1, column=0, sticky="w", padx=10)
        link_label.bind("<Button-1>", lambda e: webbrowser.open(url))

    def update_technical_section(self, mod_data):
        """Updates the Technical section with environment, provides, suggests."""
        technical_frame = self.sections['Technical']['frame']
        self.create_dedicated_block(technical_frame, "Environment", mod_data.get("environment", "Unknown"), 0)
        self.create_dedicated_block(technical_frame, "Provides", mod_data.get("provides", {}), 1, list_mode=True)
        self.create_dedicated_block(technical_frame, "Suggests", mod_data.get("suggests", {}), 2, list_mode=True)

