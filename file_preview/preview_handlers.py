from abc import abstractmethod, ABC

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel


class PreviewHandler(ABC):
    @abstractmethod
    def can_handle(self, path: str) -> bool:
        ...

    @abstractmethod
    def widget(self) -> QWidget:
        ...

    @abstractmethod
    def preview(self, path: str):
        ...


class FallbackPreviewHandler(PreviewHandler):
    def __init__(self):
        self._widget = QLabel("No preview available.")
        self._widget.setAlignment(Qt.AlignCenter)
        self._widget.setWordWrap(True)

    def can_handle(self, path: str) -> bool:
        return True  # Fallback is strong boi, he can handle anything

    def widget(self):
        return self._widget

    def preview(self, path: str):
        self._widget.setText(f"No preview available for:\n{path}")
