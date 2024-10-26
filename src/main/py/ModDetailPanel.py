from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame, QGridLayout, QHBoxLayout  # Added QHBoxLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import os

class ModDetailPanel(QWidget):
    """Handles the display and updating of the mod details."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Remove any width constraints
        self.setSizePolicy(self.sizePolicy().Expanding, self.sizePolicy().Expanding)

        # Scroll area setup for mod details
        self.layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        # Main scroll content container
        self.scroll_content = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        # Dictionary to hold sections for dynamic updates
        self.sections = {}

        # Add and position the icon label at the top (aligned left)
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # Align icon to top-left corner
        self.scroll_layout.addWidget(self.icon_label, 0, 0, 1, 1)

        # Create categories with headers
        self.create_category_header("General", 1, default_open=True)
        self.create_category_header("Compatibility", 3, default_open=True)
        self.create_category_header("Contact", 5, default_open=True)
        self.create_category_header("Technical", 7, default_open=False)

    def create_category_header(self, title, row, default_open=True):
        """Creates a collapsible category header with an arrow and title label on the same line."""

        # Create a horizontal layout for the header to align the arrow and title in one row
        header_frame = QFrame(self.scroll_content)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for tighter spacing

        # Arrow label for toggle functionality
        arrow_label = QLabel("▼" if default_open else "▲")
        arrow_label.setStyleSheet("font-size: 12pt;")
        header_layout.addWidget(arrow_label)

        # Title label for the category (clickable)
        category_label = QLabel(f"<u>{title}</u>")
        category_label.setStyleSheet("font-size: 12pt; cursor: pointer;")
        category_label.mousePressEvent = lambda event, sec=title: self.toggle_section(sec)
        header_layout.addWidget(category_label)

        # Align items to the left
        header_layout.addStretch()

        # Section content frame with vertical layout
        section_frame = QFrame(self.scroll_content)
        section_layout = QVBoxLayout(section_frame)
        section_frame.setLayout(section_layout)

        # Store section info for toggling
        self.sections[title] = {'frame': section_frame, 'open': default_open, 'arrow': arrow_label, 'row': row + 1}

        # Initial visibility
        section_frame.setVisible(default_open)
        self.scroll_layout.addWidget(header_frame, row, 0, 1, 2)
        self.scroll_layout.addWidget(section_frame, row + 1, 0, 1, 2)

    def toggle_section(self, section_name):
        """Toggles the visibility of a section."""
        section = self.sections[section_name]
        is_open = section['open']
        section['frame'].setVisible(not is_open)
        section['arrow'].setText("▼" if not is_open else "▲")
        section['open'] = not is_open

    def update_display(self, mod_data):
        """Clears current data and updates display with the new mod details based on mod_id."""
        if not mod_data:
            print("No data found for the selected mod.")
            return

        self.clear_all_sections()  # Clear previous display
        self.update_icon(mod_data)
        self.update_general_section(mod_data)
        self.update_compatibility_section(mod_data)
        self.update_contact_section(mod_data.get("contact", {}))
        self.update_technical_section(mod_data)

    def clear_all_sections(self):
        """Clears all data in each section."""
        for section in self.sections.values():
            self.clear_section(section['frame'])

    def clear_section(self, frame):
        """Clears widgets in a section frame."""
        for i in reversed(range(frame.layout().count())):
            widget = frame.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def update_icon(self, mod_data):
        """Loads and sets the mod icon aligned to the left."""
        icon_path = mod_data.get("icon_path")
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio)
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.clear()  # Clear if icon not available

    def update_general_section(self, mod_data):
        """Updates the General section with mod data, ensuring word wrap for text fields."""
        general_frame = self.sections['General']['frame']
        self.create_dedicated_block(general_frame, "Mod ID", mod_data.get("id", "Unknown"))
        self.create_dedicated_block(general_frame, "Mod Name", mod_data.get("name", "Unknown"))
        self.create_dedicated_block(general_frame, "Version", mod_data.get("version", "Unknown"))

        # Wrap the description text
        self.create_dedicated_block(general_frame, "Description", mod_data.get("description", "No description available"), wrap_text=True)

    def create_dedicated_block(self, frame, label_text, value, list_mode=False, wrap_text=False):
        """Creates a field label and value display, with optional word wrapping for text."""
        label = QLabel(f"<b>{label_text}:</b>")
        frame.layout().addWidget(label)

        if list_mode and isinstance(value, dict):
            for mod, version in value.items():
                mod_label = QLabel(f"{mod} {version}")
                frame.layout().addWidget(mod_label)
        else:
            value_label = QLabel(value)
            if wrap_text:
                value_label.setWordWrap(True)  # Enable word wrapping for long text
            frame.layout().addWidget(value_label)

    def update_compatibility_section(self, mod_data):
        """Updates the Compatibility section with dependency data."""
        compatibility_frame = self.sections['Compatibility']['frame']
        self.create_dedicated_block(compatibility_frame, "Depends", mod_data.get("depends", {}), list_mode=True)
        self.create_dedicated_block(compatibility_frame, "Recommends", mod_data.get("recommends", {}), list_mode=True)
        self.create_dedicated_block(compatibility_frame, "Breaks", mod_data.get("breaks", {}), list_mode=True)
        self.create_dedicated_block(compatibility_frame, "Conflicts", mod_data.get("conflicts", {}), list_mode=True)

    def update_contact_section(self, contact_data):
        """Dynamically updates the Contact section with provided contact info."""
        contact_frame = self.sections['Contact']['frame']
        contact_fields = ['homepage', 'sources', 'issues', 'email', 'irc', 'discord']
        self.clear_section(contact_frame)

        for field in contact_fields:
            if field in contact_data:
                self.create_clickable_label(contact_frame, field.capitalize(), contact_data[field])

    def create_clickable_label(self, frame, label_text, url):
        """Creates a clickable label for a URL."""
        label = QLabel(f"<b>{label_text}:</b>")
        frame.layout().addWidget(label)
        link_label = QLabel(f"<a href='{url}'>{url}</a>")
        link_label.setOpenExternalLinks(True)
        frame.layout().addWidget(link_label)

    def update_technical_section(self, mod_data):
        """Updates the Technical section with technical data."""
        technical_frame = self.sections['Technical']['frame']
        self.create_dedicated_block(technical_frame, "Environment", mod_data.get("environment", "Unknown"))
        self.create_dedicated_block(technical_frame, "Provides", mod_data.get("provides", {}), list_mode=True)
        self.create_dedicated_block(technical_frame, "Suggests", mod_data.get("suggests", {}), list_mode=True)
