# MainGui.py
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QMenuBar, QAction, QFileDialog,
    QSplitter, QHBoxLayout, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ModDetailPanel import ModDetailPanel
from ModListPanel import ModListPanel
from VersionControlPanel import VersionControlPanel
from ConfigHandler import ConfigHandler
import os
import json
import shutil
import subprocess

class ModDependencyListerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MC ZPatcher")
        self.setGeometry(100, 100, 1200, 800)
        self.selected_folder = None  # Store the folder path

        # Load or create config
        self.config_handler = ConfigHandler()
        self.config = self.config_handler.load_or_create_config()

        # Central widget setup
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # Initialize UI components
        self.init_ui()
        self.create_menu()

        # Handle application closing to clean up
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.closeEvent = self.on_exit  # Connect close event

    def init_ui(self):
        # Main splitter to handle resizing between panels
        self.main_splitter = QSplitter(Qt.Horizontal)

        # Mod List Panel (initialize first)
        self.mod_detail_panel = ModDetailPanel()  # Initialize detail panel here for completeness
        self.mod_list_panel = ModListPanel(mod_detail_panel=self.mod_detail_panel)

        # Version Control Panel (first on the left, now that mod_list_panel is available)
        self.version_control_panel = VersionControlPanel(
            self,
            mod_list_panel=self.mod_list_panel  # Pass reference to mod_list_panel
        )
        self.main_splitter.addWidget(self.version_control_panel)

        # Add Mod List Panel (center)
        self.main_splitter.addWidget(self.mod_list_panel)

        # Add Mod Detail Panel (right)
        self.main_splitter.addWidget(self.mod_detail_panel)

        # Ensure proper layout positioning
        self.main_layout.addWidget(self.main_splitter)
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 4)
        self.main_splitter.setStretchFactor(2, 2)

    def create_menu(self):
        # Menu bar setup
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)

        # "File" menu
        file_menu = self.menu_bar.addMenu("File")
        open_folder_action = QAction("Open Mods Folder", self)
        open_folder_action.triggered.connect(self.select_folder)
        file_menu.addAction(open_folder_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # "View" menu
        view_menu = self.menu_bar.addMenu("View")

        # Panels Submenu
        panels_menu = view_menu.addMenu("Panels")

        # Detail Panel submenu
        detail_panel_menu = panels_menu.addMenu("Detail Panel")
        toggle_detail_panel_action = QAction("Enabled", self, checkable=True)
        toggle_detail_panel_action.setChecked(self.config['detailpane']['enabled'])
        toggle_detail_panel_action.triggered.connect(self.toggle_detail_panel)
        detail_panel_menu.addAction(toggle_detail_panel_action)

        popout_detail_panel_action = QAction("Popout", self, checkable=True)
        popout_detail_panel_action.setChecked(self.config['detailpane']['popout'])
        popout_detail_panel_action.triggered.connect(self.toggle_detail_popout)
        detail_panel_menu.addAction(popout_detail_panel_action)

        # Version Control Panel submenu
        version_panel_menu = panels_menu.addMenu("Version Control Panel")
        toggle_version_panel_action = QAction("Enabled", self, checkable=True)
        toggle_version_panel_action.setChecked(self.config['versionpane']['enabled'])
        toggle_version_panel_action.triggered.connect(self.toggle_version_panel)
        version_panel_menu.addAction(toggle_version_panel_action)

        popout_version_panel_action = QAction("Popout", self, checkable=True)
        popout_version_panel_action.setChecked(self.config['versionpane']['popout'])
        popout_version_panel_action.triggered.connect(self.toggle_version_popout)
        version_panel_menu.addAction(popout_version_panel_action)

    def find_on_curseforge_callback(self):
        """Callback to trigger CurseForge search from the VersionControlPanel."""
        self.version_control_panel.initiate_curseforge_sync(self.mod_list_panel.mod_info)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Mods Folder")
        if folder_path:
            self.selected_folder = folder_path

            if os.path.exists("mod_temp_data"):
                shutil.rmtree("mod_temp_data")

            jar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'build', 'libs', 'MC-ZPatcher.jar')
            if not os.path.exists(jar_path):
                QMessageBox.critical(self, "Error", f"JAR file not found at {jar_path}")
                return

            try:
                result = subprocess.run(
                    ['java', '--enable-preview', '-jar', jar_path, folder_path],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                if result.returncode != 0:
                    QMessageBox.critical(self, "Error", f"Java process failed:\n{result.stderr}")
                    return

                # Load mod data without querying CurseForge
                self.load_mod_data("mod_temp_data/mod_data.json")

                # Enable the Find on CurseForge button after loading mods
                self.enable_find_button()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error accessing JAR file: {e}")

    def load_mod_data(self, json_file):
        """Loads mod data from a JSON file without querying CurseForge."""
        try:
            with open(json_file, 'r') as f:
                mod_data = json.load(f)

            # Populate mod list without querying CurseForge
            self.mod_list_panel.populate_mod_list(mod_data)

            # Update the Mods Found label
            mods_found_count = len(mod_data)
            self.version_control_panel.update_mod_counts(
                mods_found=mods_found_count,
                up_to_date=0,  # Placeholder
                outdated=0,    # Placeholder
                curseforge_sync=0,  # Sync will happen when button is clicked
                modrinth_sync=0  # Placeholder
            )

        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"File {json_file} not found.")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Error decoding JSON data: {e}")

    def enable_find_button(self):
        """Enable the 'Find on CurseForge' button once mods are loaded."""
        self.version_control_panel.update_find_button_state("normal")

    def toggle_detail_panel(self):
        enabled = self.config['detailpane']['enabled']
        self.config['detailpane']['enabled'] = not enabled
        self.config_handler.save_config(self.config)
        self.mod_detail_panel.setVisible(not enabled)

    def toggle_detail_popout(self):
        self.config['detailpane']['popout'] = not self.config['detailpane']['popout']
        self.config_handler.save_config(self.config)

    def toggle_version_panel(self):
        enabled = self.config['versionpane']['enabled']
        self.config['versionpane']['enabled'] = not enabled
        self.config_handler.save_config(self.config)
        self.version_control_panel.setVisible(not enabled)

    def toggle_version_popout(self):
        self.config['versionpane']['popout'] = not self.config['versionpane']['popout']
        self.config_handler.save_config(self.config)

    def on_exit(self, event=None):
        """Cleans up temporary files and handles app exit."""
        if os.path.exists("mod_temp_data"):
            shutil.rmtree("mod_temp_data")
        QApplication.instance().quit()

if __name__ == "__main__":
    app = QApplication([])
    window = ModDependencyListerApp()
    window.show()
    app.exec_()
