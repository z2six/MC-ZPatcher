# ModListPanel.py
import tkinter as tk
from tkinter import ttk, Scrollbar

class ModListPanel:
    def __init__(self, parent, on_mod_select, on_checkbox_click, icons):
        """Initializes the mod list section with icons."""
        self.parent = parent
        self.on_mod_select = on_mod_select
        self.on_checkbox_click = on_checkbox_click
        self.icons = icons  # Store the icons dictionary

        # Create the mod list frame
        self.mod_list_frame = tk.Frame(self.parent)

        # Treeview to display mod list with added CF Sync column
        self.tree = ttk.Treeview(self.mod_list_frame, columns=("Enabled", "Mod ID", "Mod Name", "Modloader", "Version", "CF Sync"), show="headings")
        self.tree.heading("Enabled", text="Enabled")
        self.tree.heading("Mod ID", text="Mod ID")
        self.tree.heading("Mod Name", text="Mod Name")
        self.tree.heading("Modloader", text="Modloader")
        self.tree.heading("Version", text="Version")
        self.tree.heading("CF Sync", text="CF Sync")  # New column for CurseForge Sync status

        # Set fixed column widths
        self.tree.column("Enabled", width=65)
        self.tree.column("Mod ID", width=150)
        self.tree.column("Mod Name", width=250)
        self.tree.column("Modloader", width=150)
        self.tree.column("Version", width=100)
        self.tree.column("CF Sync", width=75)  # Column for CF Sync status

        self.tree.grid(row=0, column=0, sticky="nsew")

        # Add vertical and horizontal scrollbars
        self.mod_list_scrollbar_y = Scrollbar(self.mod_list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.mod_list_scrollbar_y.set)
        self.mod_list_scrollbar_y.grid(row=0, column=1, sticky="ns")

        self.mod_list_scrollbar_x = Scrollbar(self.mod_list_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(xscrollcommand=self.mod_list_scrollbar_x.set)
        self.mod_list_scrollbar_x.grid(row=1, column=0, sticky="ew")

        # Allow dynamic resizing of the mod list
        self.mod_list_frame.grid_rowconfigure(0, weight=1)
        self.mod_list_frame.grid_columnconfigure(0, weight=1)

        # Bind mod selection events
        self.tree.bind("<ButtonRelease-1>", self.on_mod_select)

        # Bind checkboxes to click events
        self.tree.bind("<Button-1>", self.on_checkbox_click)

        # Dictionary to hold icon labels for each row
        self.icon_labels = {}

    def populate_mod_list(self, mod_data):
        """Populates the mod list with the provided mod data."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        self.mod_info = mod_data

        # Remove any existing labels
        for label in self.icon_labels.values():
            label.destroy()
        self.icon_labels.clear()

        # Add each mod to the Treeview and overlay an icon label
        for mod in self.mod_info:
            enabled = "☑" if mod.get("enabled", True) else "☐"
            mod_id = mod.get("id", "Unknown")
            mod_name = mod.get("name", mod_id)
            modloader = mod.get("modloader", "Unknown")
            version = mod.get("version", "Unknown")

            # Insert each mod row and get its item ID
            item_id = self.tree.insert("", "end", values=(enabled, mod_id, mod_name, modloader, version, ""))

            # Call a function to position the default icon in the CF Sync column for this row
            self._place_icon_for_row(item_id, "default")

    def _place_icon_for_row(self, item_id, icon_key):
        """Helper method to place an icon in the CF Sync column for a given row item."""
        # Use bbox to get coordinates and dimensions of the CF Sync cell
        bbox = self.tree.bbox(item_id, column="CF Sync")
        if bbox:
            x, y, width, height = bbox
            icon = self.icons[icon_key]
            # Center the icon within the cell
            x_centered = x + (width - icon.width()) // 2
            y_centered = y + (height - icon.height()) // 2

            # Create the label if not exists, or update the image if it does
            if item_id in self.icon_labels:
                self.icon_labels[item_id].config(image=icon)
                self.icon_labels[item_id].place(x=x_centered, y=y_centered)
            else:
                label = tk.Label(self.tree, image=icon, borderwidth=0)
                label.place(x=x_centered, y=y_centered)
                self.icon_labels[item_id] = label

    def update_cf_sync_status(self, mod_id, status_key):
        """Updates the CF Sync status icon for a specific mod."""
        icon = self.icons.get(status_key, self.icons["default"])

        # Find the row by mod_id and update the corresponding icon label
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, "values")
            if values[1] == mod_id:  # Check if mod_id matches
                self._place_icon_for_row(item_id, status_key)  # Update icon placement
                break

    def toggle_mod(self, item):
        """Enables or disables a mod by renaming the file and updating mod_data.json."""
        values = self.tree.item(item, "values")
        mod_id = values[1]  # Extract mod ID from selected row
        selected_mod_data = next((mod for mod in self.mod_info if mod.get("id") == mod_id), None)

        if selected_mod_data:
            mod_file = selected_mod_data.get("file_path")
            enabled = selected_mod_data.get("enabled")

            if mod_file:
                try:
                    # Check current file name and toggle between enabled/disabled states
                    if enabled:
                        new_mod_file = mod_file + ".disabled"
                        os.rename(mod_file, new_mod_file)  # Rename the file
                        self.tree.set(item, "Enabled", "☐")  # Update Treeview checkbox
                    else:
                        new_mod_file = mod_file.replace(".disabled", "")
                        os.rename(mod_file, new_mod_file)
                        self.tree.set(item, "Enabled", "☑")

                    # Update mod file path and enabled status
                    selected_mod_data["file_path"] = new_mod_file
                    selected_mod_data["enabled"] = not new_mod_file.endswith(".disabled")

                    # Update the mod_data.json file (pseudo-code: modify this based on your actual file structure)
                    self.update_mod_data_json()

                except Exception as e:
                    print(f"Error renaming mod file: {e}")

    def update_mod_data_json(self):
        """Update the mod_data.json file after renaming mod files."""
        try:
            with open("mod_temp_data/mod_data.json", "w") as f:
                json.dump(self.mod_info, f, indent=4)  # Save updated mod info back to JSON file
        except Exception as e:
            print(f"Error updating mod_data.json: {e}")

    def get_frame(self):
        """Returns the frame that contains the mod list."""
        return self.mod_list_frame

    def on_middle_click_scroll(self, event):
        """Start scrolling with middle mouse button."""
        self.scroll_start_x = event.x
        self.scroll_start_y = event.y

    def on_middle_drag_scroll(self, event):
        """Handles middle mouse button dragging to scroll both horizontally and vertically."""
        delta_x = event.x - self.scroll_start_x
        delta_y = event.y - self.scroll_start_y

        # Invert the direction of scrolling
        self.tree.xview_scroll(int(delta_x / 2), "units")  # Inverted horizontal scrolling
        self.tree.yview_scroll(int(delta_y / 2), "units")  # Inverted vertical scrolling

        self.scroll_start_x = event.x
        self.scroll_start_y = event.y

    def on_enter_mod_list(self, event):
        """Enable mouse wheel scrolling for this panel when the mouse is inside."""
        self.tree.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def on_leave_mod_list(self, event):
        """Disable mouse wheel scrolling for this panel when the mouse leaves."""
        self.tree.unbind_all("<MouseWheel>")

    def on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling."""
        self.tree.yview_scroll(-1 * int(event.delta / 120), "units")
