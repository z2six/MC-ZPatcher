# ConfigHandler.py
import os
import json

class ConfigHandler:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.default_config = {
            "detailpane": {
                "enabled": True,
                "popout": False
            },
            "listpane": {
                "columns": ["enabled", "modid", "modname", "modloader", "version"]
            },
            "versionpane": {
                "enabled": True,
                "popout": False
            }
        }

    def load_or_create_config(self):
        """Load the config file if it exists, otherwise create it with default values."""
        if not os.path.exists(self.config_file):
            print(f"Config file not found. Generating default {self.config_file}.")
            self.save_config(self.default_config)
        else:
            print(f"Loading existing {self.config_file}.")
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.default_config

    def save_config(self, config_data):
        """Save the config data to the config file."""
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=4)