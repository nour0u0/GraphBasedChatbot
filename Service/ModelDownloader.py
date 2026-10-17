
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar
)

from sentence_transformers import SentenceTransformer


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_DIR = PROJECT_DIR /".."/ "EmbeddinModel" / "all-MiniLM-L6-v2"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class ModelWorker(QThread):
    status_changed = pyqtSignal(str)
    model_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            if MODEL_DIR.exists() and any(MODEL_DIR.iterdir()):
                self.status_changed.emit(
                    f"Loading local model:\n{MODEL_DIR}"
                )
                model = SentenceTransformer(str(MODEL_DIR))

            else:
                self.status_changed.emit(
                    f"Downloading model:\n{MODEL_NAME}"
                )

                MODEL_DIR.parent.mkdir(
                    parents=True, exist_ok=True
                )

                model = SentenceTransformer(MODEL_NAME)

                self.status_changed.emit(
                    "Saving model locally..."
                )
                model.save(str(MODEL_DIR))

                self.status_changed.emit(
                    f"Model saved to:\n{MODEL_DIR}"
                )

            self.model_ready.emit(model)

        except Exception as error:
            self.error_occurred.emit(str(error))


class ModelDownloader(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Agriculture Assistant - Model Setup")
        self.setFixedSize(480, 220)
        self.model = None
        self.error_message = None

        self.setStyleSheet("""
            QDialog {
                background-color: #101827;
                color: #E5EAF3;
            }

            QLabel {
                color: #CBD5E1;
                font-size: 13px;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                border: 1px solid #3B82F6;
                border-radius: 7px;
                padding: 9px 15px;
            }

            QProgressBar {
                background-color: #172235;
                border: 1px solid #34445C;
                border-radius: 6px;
                height: 18px;
                text-align: center;
                color: #E5EAF3;
            }

            QProgressBar::chunk {
                background-color: #3B82F6;
                border-radius: 5px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Preparing AI Model")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: 700;
            color: #60A5FA;
        """)
        layout.addWidget(title)

        self.status_label = QLabel(
            "Checking whether the model is available..."
        )
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setFormat("Please wait...")
        layout.addWidget(self.progress)

        self.worker = ModelWorker(self)
        self.worker.status_changed.connect(
            self.status_label.setText
        )
        self.worker.model_ready.connect(
            self.on_model_ready
        )
        self.worker.error_occurred.connect(
            self.on_error
        )
        self.worker.start()

    def on_model_ready(self, model):
        self.model = model
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.progress.setFormat("Complete")
        self.status_label.setText(
            "Model ready. Starting the application..."
        )
        self.accept()

    def on_error(self, message):
        self.error_message = message
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat("Failed")
        self.status_label.setText(
            f"Model setup failed:\n{message}"
        )

    def closeEvent(self, event):
        if self.worker.isRunning():
            event.ignore()
            self.status_label.setText(
                "Please wait for model setup to finish."
            )
        else:
            event.accept()
