from abc import abstractmethod, ABC

import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QSizePolicy, QVBoxLayout


class PreviewHandler(ABC):
    def __init__(self):
        self.supported_extensions: list[str] = []

    def can_handle(self, path: str) -> bool:
        return any(path.endswith(ext) for ext in self.supported_extensions)

    @abstractmethod
    def widget(self) -> QWidget:
        ...

    @abstractmethod
    def preview(self, path: str):
        ...


class FallbackPreviewHandler(PreviewHandler):
    def __init__(self):
        super().__init__()
        self._widget = QLabel("No preview available.")
        self._widget.setAlignment(Qt.AlignCenter)
        self._widget.setWordWrap(True)

    def can_handle(self, path: str) -> bool:
        return True  # Fallback is strong boi, he can handle anything

    def widget(self):
        return self._widget

    def preview(self, path: str):
        self._widget.setText(f"No preview available for:\n{path}")


class TextPreviewHandler(PreviewHandler):
    def __init__(self):
        super().__init__()
        self.supported_extensions = [
            ".txt", ".log", ".csv", ".md", ".ini", ".cfg",
            ".json", ".yaml", ".yml", ".py", ".c", ".cpp", ".h", ".java", ".js", ".ts", ".html", ".xml"
        ]
        # Use a QTextEdit for text display
        self._widget = QTextEdit("")
        self._widget.setReadOnly(True)

    def widget(self) -> QWidget:
        return self._widget

    def preview(self, path: str):
        with open(path, "r") as f:
            content = f.read()
        self._widget.setText(content)


class ImagePreviewHandler(PreviewHandler):
    def __init__(self):
        super().__init__()
        self.supported_extensions = [
            ".bmp", ".gif", ".jpg", ".jpeg", ".png", ".pbm", ".pgm", ".ppm", ".xbm", ".xpm"
        ]
        # Use a QLabel for image display
        self._widget = QLabel()
        self._widget.setAlignment(Qt.AlignCenter)
        self._widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)  # Let splitter control size
        self._widget.setScaledContents(False)  # Preserve aspect ratio unless you override

    def widget(self) -> QWidget:
        return self._widget

    def preview(self, path: str):
        pix = QPixmap()
        if pix.load(path):
            # Scale the image to fit the label, keeping aspect ratio
            scaled = pix.scaled(self._widget.width(), self._widget.height(), Qt.AspectRatioMode.KeepAspectRatio)
            self._widget.setPixmap(scaled)
        else:
            self._widget.setText(f"Unable to load image: {path}")


class OpenCVVideoPreviewHandler(PreviewHandler):
    def __init__(self):
        super().__init__()
        self.supported_extensions = [".mp4", ".avi", ".mov", ".mkv"]

        self._container = QWidget()
        layout = QVBoxLayout(self._container)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel("Loading video preview...")
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setStyleSheet("background-color: black;")
        layout.addWidget(self._label)

        self._timer = QTimer()
        self._timer.timeout.connect(self._next_frame)

        self._cap = None
        self._frame_count = 0
        self._max_frames = 0

    def widget(self):
        return self._container

    def preview(self, path: str):
        if self._cap:
            self._cap.release()
        self._cap = cv2.VideoCapture(path)
        if not self._cap.isOpened():
            self._label.setText("Unable to open video.")
            return

        fps = self._cap.get(cv2.CAP_PROP_FPS)
        self._max_frames = int(fps * 3)  # 3 seconds
        self._frame_count = 0
        self._timer.start(int(1000 / fps))

    def _next_frame(self):
        if self._frame_count >= self._max_frames:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # rewind to frame 0
            self._frame_count = 0
            return  # optional: skip redraw this cycle for smoothness

        ret, frame = self._cap.read()
        if not ret:
            self._label.setText("Failed to read video frame.")
            self._timer.stop()
            return

        # Convert BGR (OpenCV) → RGB (Qt)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(self._label.width(), self._label.height(), Qt.KeepAspectRatio,
                                            Qt.SmoothTransformation)
        self._label.setPixmap(pix)

        self._frame_count += 1
