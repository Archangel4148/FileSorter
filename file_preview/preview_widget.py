from PyQt5.QtWidgets import QWidget, QStackedLayout

from file_preview.preview_handlers import FallbackPreviewHandler, TextPreviewHandler, ImagePreviewHandler, \
    OpenCVVideoPreviewHandler, ZipPreviewHandler


class FilePreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QStackedLayout()
        self.setLayout(self._layout)

        self.handlers = [
            TextPreviewHandler(),
            ImagePreviewHandler(),
            OpenCVVideoPreviewHandler(),
            ZipPreviewHandler(),
        ]
        self.fallback_handler = FallbackPreviewHandler()
        self._layout.addWidget(self.fallback_handler.widget())

    def preview(self, path: str):
        for handler in self.handlers:
            if handler.can_handle(path):
                widget = handler.widget()
                if self._layout.indexOf(widget) == -1:
                    self._layout.addWidget(widget)
                self._layout.setCurrentWidget(widget)
                handler.preview(path)
                return

        self._layout.setCurrentWidget(self.fallback_handler.widget())
        self.fallback_handler.preview(path)
