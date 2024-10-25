import tkinter as tk
from tkinter import Toplevel, Checkbutton, BooleanVar, Label, Button

class ColumnSetting:
    def __init__(self, root, config_handler, config):
        self.root = root
        self.config_handler = config_handler
        self.config = config
        self.column_window = None

        # Define all available columns and their categories
        self.columns = {
            "General": ["Enabled", "Mod ID", "Name", "Description", "Mod Loader", "Provides", "Environment", "Version", "JARs", "Language Adapters"],
            "Entrypoints": ["Entrypoints > Main", "Entrypoints > Client", "Entrypoints > Server"],
            "Mixins": ["Mixins > config", "Mixins > Environment"],
            "Dependencies": ["Dependencies", "Recommends", "Suggests", "Breaks", "Conflicts"],
            "Contact": ["Contact", "Contact > Email", "Contact > irc", "Contact > Homepage", "Contact > Issues", "Contact > Sources"],
            "Authors": ["Authors", "Authors > Name", "Authors > Contact"],
            "Contributors": ["Contributors"],
            "License": ["License"]
        }

        # Holds the BooleanVar values for each checkbox
        self.column_vars = {}

    def open_column_window(self):
        """Open a window to toggle columns for the Mod List Panel."""
        self.column_window = Toplevel(self.root)
        self.column_window.title("Toggle Columns")
        self.column_window.geometry("500x400")
        self.column_window.minsize(500, 400)

        self.create_column_checkboxes()

        # Add Save and Cancel buttons at the bottom
        button_frame = tk.Frame(self.column_window)
        button_frame.grid(row=10, column=0, columnspan=3, pady=10)

        save_button = Button(button_frame, text="Save", command=self.save_columns)
        save_button.pack(side="left", padx=10)
        cancel_button = Button(button_frame, text="Cancel", command=self.column_window.destroy)
        cancel_button.pack(side="right", padx=10)

    def create_column_checkboxes(self):
        """Create checkboxes for each column option and arrange them in rows and columns."""
        row = 0
        col = 0

        # Loop through categories and add labels and checkboxes
        for category, options in self.columns.items():
            if col > 2:  # Move to the next row of categories after 3 columns
                col = 0
                row += 1

            # Add category label
            category_label = Label(self.column_window, text=category, font=("Arial", 12, "bold"))
            category_label.grid(row=row, column=col, sticky="w", padx=10, pady=(10, 5))
            row += 1

            for option in options:
                var = BooleanVar()
                var.set(option.lower() in self.config['listpane']['columns'])  # Pre-load config settings
                checkbox = Checkbutton(self.column_window, text=option, variable=var)
                checkbox.grid(row=row, column=col, sticky="w", padx=20)
                self.column_vars[option] = var
                row += 1

            # Reset the row and move to the next column after each category
            row = 0
            col += 1

    def save_columns(self):
        """Save the selected columns to config and update the config file."""
        selected_columns = []

        for option, var in self.column_vars.items():
            if var.get():
                # Convert column names to lowercase and standardize keys for storage
                standardized_key = option.lower().replace(" > ", "_").replace(" ", "")
                selected_columns.append(standardized_key)

        self.config['listpane']['columns'] = selected_columns
        self.config_handler.save_config(self.config)
        self.column_window.destroy()
