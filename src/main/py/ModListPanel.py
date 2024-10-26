# ModListPanel.py
from PyQt5.QtWidgets import (
    QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout, QAbstractItemView, QScrollBar
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal
import os

class ModListPanel(QWidget):
    # Signal to trigger icon update on the main thread
    update_icon_signal = pyqtSignal(str, str)  # Pass unique_id and status_key

    def __init__(self, mod_detail_panel=None):
        super().__init__()
        self.mod_detail_panel = mod_detail_panel

        # Load icons for CF Sync status (assuming images are in `../resources/icons`)
        icon_folder = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons')
        self.enabled_icon = QIcon(os.path.join(icon_folder, "enabled.png"))
        self.disabled_icon = QIcon(os.path.join(icon_folder, "disabled.png"))
        self.icon_default = QIcon(os.path.join(icon_folder, "orange_question.png"))
        self.icon_searching = QIcon(os.path.join(icon_folder, "blue_sync.png"))
        self.icon_found = QIcon(os.path.join(icon_folder, "green_checkmark.png"))
        self.icon_not_found = QIcon(os.path.join(icon_folder, "red_cross.png"))

        # Set up layout and table widget
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Enabled", "Mod ID", "Mod Name", "Modloader", "Version", "CF Sync"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Define column widths for better visual formatting
        self.table.setColumnWidth(0, 65)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 250)
        self.table.setColumnWidth(3, 150)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 75)

        # Scrollbars
        self.table.setVerticalScrollBar(QScrollBar())
        self.table.setHorizontalScrollBar(QScrollBar())

        # Connect row selection to handle_mod_select
        self.table.itemSelectionChanged.connect(self.handle_mod_select)

        # Add table to layout
        self.layout.addWidget(self.table)
        self.mod_info = []  # Store loaded mod data, including unique_id

        # Enable icon click functionality for toggling
        self.table.cellClicked.connect(self.handle_icon_click)

        # Connect the signal to the update method
        self.update_icon_signal.connect(self.update_cf_sync_status)

    def populate_mod_list(self, mod_data):
        """Populates the mod list with the provided mod data."""
        self.table.setRowCount(0)
        self.mod_info = mod_data  # Store mod data with unique_id in memory
        print("ModListPanel - mod_info populated:", self.mod_info)

        for mod in self.mod_info:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            # Determine enabled status from file name
            enabled = not mod.get("file_path", "").endswith(".disabled")
            mod["enabled"] = enabled

            # Set icon based on enabled/disabled state
            enabled_item = QTableWidgetItem()
            enabled_item.setIcon(self.enabled_icon if enabled else self.disabled_icon)
            self.table.setItem(row_position, 0, enabled_item)
            self.table.setItem(row_position, 1, QTableWidgetItem(mod.get("id", "Unknown")))
            self.table.setItem(row_position, 2, QTableWidgetItem(mod.get("name", "Unknown")))
            self.table.setItem(row_position, 3, QTableWidgetItem(mod.get("modloader", "Unknown")))
            self.table.setItem(row_position, 4, QTableWidgetItem(mod.get("version", "Unknown")))

            # Add CF Sync icon (set default initially)
            self._set_icon_for_row(row_position, self.icon_default)

            # Store unique_id directly in mod_info for consistent referencing
            mod["unique_id"] = mod.get("unique_id", "Unknown")

    def _set_icon_for_row(self, row_position, icon):
        """Helper method to set an icon in the CF Sync column for a given row."""
        icon_item = QTableWidgetItem()
        icon_item.setIcon(icon)
        self.table.setItem(row_position, 5, icon_item)

    def handle_mod_select(self):
        """Handles row selection and notifies ModDetailPanel of the selected mod data."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            print("No row selected.")
            return

        # Retrieve the mod data for the selected row
        mod_id = self.table.item(selected_row, 1).text()
        selected_mod_data = next((mod for mod in self.mod_info if mod.get("id") == mod_id), None)

        if selected_mod_data:
            # Notify ModDetailPanel to update itself with the selected mod's data
            if self.mod_detail_panel:
                self.mod_detail_panel.update_display(selected_mod_data)

    def handle_icon_click(self, row, column):
        """Handles icon click to toggle enabled/disabled state if clicked on the Enabled column."""
        if column == 0:  # Enabled column
            mod_id = self.table.item(row, 1).text()
            selected_mod_data = next((mod for mod in self.mod_info if mod.get("id") == mod_id), None)
            if selected_mod_data:
                self.toggle_mod_enabled(selected_mod_data, row)

    def toggle_mod_enabled(self, mod_data, row):
        """Toggles the enabled/disabled state of the mod file by renaming it."""
        file_path = mod_data.get("file_path")
        if not file_path or not os.path.isfile(file_path):
            print("File path invalid or file does not exist.")
            return

        # Determine new file path and rename based on current state
        if file_path.endswith(".disabled"):
            new_file_path = file_path[:-9]  # Remove ".disabled"
            mod_data["enabled"] = True
            self.table.item(row, 0).setIcon(self.enabled_icon)
        else:
            new_file_path = file_path + ".disabled"
            mod_data["enabled"] = False
            self.table.item(row, 0).setIcon(self.disabled_icon)

        try:
            os.rename(file_path, new_file_path)
            mod_data["file_path"] = new_file_path
            print(f"File renamed to: {new_file_path}")
        except OSError as e:
            print(f"Error renaming file: {e}")

    def update_cf_sync_status(self, unique_id, status_key):
        """Updates the CF Sync status icon in the table for a specific mod by unique_id."""
        # Determine the icon based on the status key
        icon = {
            "default": self.icon_default,
            "searching": self.icon_searching,
            "found": self.icon_found,
            "not_found": self.icon_not_found
        }.get(status_key, self.icon_default)

        # Find the row with the matching unique_id and update its icon
        for row in range(self.table.rowCount()):
            if self.mod_info[row].get("unique_id") == unique_id:
                self._set_icon_for_row(row, icon)
                self.table.viewport().update()  # Force refresh
                break