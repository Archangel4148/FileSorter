import os
import sys

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QTreeWidgetItem

from file_browser_init import Ui_file_browser_window


class FileBrowserWindow(QWidget):

    def __init__(self):
        super().__init__()

        # Initialize UI
        self.ui = Ui_file_browser_window()
        self.ui.setupUi(self)

        # Load previous settings
        self.settings = QSettings("SimCorp", "FileSorter")
        self.load_settings()

        # UI connections
        self.ui.open_browser_button.clicked.connect(self.open_root_directory_dialog)
        self.ui.populate_button.clicked.connect(self.populate)

    def closeEvent(self, event):
        # Save settings on close
        self.save_settings()
        super().closeEvent(event)

    def load_settings(self):
        self.root_directory = self.settings.value("root_dir", "")

    def save_settings(self):
        self.settings.setValue("root_dir", self.root_directory)

    @property
    def root_directory(self):
        return self.ui.root_directory_line_edit.text()

    @root_directory.setter
    def root_directory(self, path: str):
        self.ui.root_directory_line_edit.setText(path)

    def open_root_directory_dialog(self):
        # Open a file dialog to select a root directory
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Directory")
        file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        file_dialog.setViewMode(QFileDialog.ViewMode.List)
        # If a directory was selected, update the UI
        if file_dialog.exec():
            self.root_directory = file_dialog.selectedFiles()[0]

    def populate(self):
        self.ui.file_tree_widget.clear()
        add_directory_contents_to_tree(self.root_directory, self.ui.file_tree_widget)


def add_directory_contents_to_tree(path: str, parent_item: QTreeWidgetItem):
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        # Add the item to the tree
        tree_item = QTreeWidgetItem(parent_item)
        tree_item.setText(0, item)
        # If the item is a directory, recurse into it
        if os.path.isdir(full_path):
            add_directory_contents_to_tree(full_path, tree_item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileBrowserWindow()
    window.show()
    sys.exit(app.exec_())
