import os
import sys

from PyQt5.QtCore import QSettings, QTimer
from PyQt5.QtWidgets import QWidget, QApplication, QFileDialog, QTreeWidgetItem, QSizePolicy

from file_browser_init import Ui_file_browser_window
from file_preview.preview_widget import FilePreviewWidget


class FileBrowserWindow(QWidget):

    def __init__(self):
        super().__init__()

        # Initialize UI
        self.ui = Ui_file_browser_window()
        self.ui.setupUi(self)

        # Create the custom preview widget
        self.preview_widget = FilePreviewWidget()
        self.ui.file_display_splitter.addWidget(self.preview_widget)
        self.preview_widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)

        # Load previous settings after UI finishes loading
        self.settings = QSettings("SimCorp", "FileSorter")
        QTimer.singleShot(0, self.load_settings)

        # UI connections
        self.ui.open_browser_button.clicked.connect(self.open_root_directory_dialog)
        self.ui.file_tree_widget.itemSelectionChanged.connect(self.handle_selection_change)

        self.preview_file_path: str = ""

    def initialize_splitter(self, left_portion: float):
        # Setup splitter (because it's stupid and bad)
        total_width = self.ui.file_display_splitter.width()
        left = int(total_width * left_portion)
        right = total_width - left
        self.ui.file_display_splitter.setSizes([left, right])

    def closeEvent(self, event):
        # Save settings on close
        self.save_settings()
        super().closeEvent(event)

    def load_settings(self):
        self.root_directory = self.settings.value("root_dir", "")
        splitter_left_fraction = float(self.settings.value("splitter_left_fraction", "0.33"))
        self.initialize_splitter(splitter_left_fraction)

    def save_settings(self):
        # Save the root directory
        self.settings.setValue("root_dir", self.root_directory)

        # Save the splitter orientation
        splitter = self.ui.file_display_splitter
        left_fraction = splitter.sizes()[0] / splitter.width()
        self.settings.setValue("splitter_left_fraction", left_fraction)

    @property
    def root_directory(self):
        return self.ui.root_directory_line_edit.text()

    @root_directory.setter
    def root_directory(self, path: str):
        self.ui.root_directory_line_edit.setText(path)
        self.populate()

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
        if self.root_directory:
            add_directory_contents_to_tree(self.root_directory, self.ui.file_tree_widget)

    def handle_selection_change(self):
        items = self.ui.file_tree_widget.selectedItems()
        if items:
            self.file_selected(items[0])

    def get_full_path_from_item(self, item: QTreeWidgetItem) -> str:
        parts = []
        # Step back to the root path, recording folders along the way
        while item is not None:
            parts.insert(0, item.text(0))
            item = item.parent()
        return os.path.normpath(os.path.join(self.root_directory, *parts))

    def file_selected(self, item: QTreeWidgetItem):
        # Update the selected path, and send it to be previewed
        self.preview_file_path = self.get_full_path_from_item(item)
        self.preview_widget.preview(self.preview_file_path)

def add_directory_contents_to_tree(path: str, parent_item: QTreeWidgetItem):
    try:
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            # Add the item to the tree
            tree_item = QTreeWidgetItem(parent_item)
            tree_item.setText(0, item)
            # If the item is a directory, recurse into it
            if os.path.isdir(full_path):
                add_directory_contents_to_tree(full_path, tree_item)
    except PermissionError:
        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileBrowserWindow()
    window.show()
    sys.exit(app.exec_())
