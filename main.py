import sys

from PyQt5.QtWidgets import QWidget, QApplication

from file_browser_init import Ui_file_browser_window


class FileBrowserWindow(QWidget):

    def __init__(self):
        super().__init__()

        # Initialize UI
        self.ui = Ui_file_browser_window()
        self.ui.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileBrowserWindow()
    window.show()
    sys.exit(app.exec_())
