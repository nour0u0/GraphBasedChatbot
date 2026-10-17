
import json
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QSpinBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QMessageBox,
)


CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


class ConfigTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            QWidget {
                background-color: #0B1120;
                color: #E5EAF3;
                font-size: 13px;
            }

            QGroupBox {
                background-color: #111827;
                border: 1px solid #263449;
                border-radius: 10px;
                margin-top: 14px;
                padding: 16px;
                font-weight: 600;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 14px;
                padding: 0 6px;
                color: #60A5FA;
            }

            QLabel {
                color: #CBD5E1;
            }

            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
                background-color: #172235;
                color: #F1F5F9;
                border: 1px solid #34445C;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #2563EB;
            }

            QLineEdit:focus, QTextEdit:focus,
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #3B82F6;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px 18px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #3B82F6;
            }

            QPushButton#secondaryButton {
                background-color: #263449;
            }

            QPushButton#secondaryButton:hover {
                background-color: #34445C;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # Header
        title = QLabel("Application Configuration")
        title.setStyleSheet(
            "font-size: 22px; font-weight: 700; color: #60A5FA;"
        )
        root.addWidget(title)

        subtitle = QLabel(
            "Configure the chatbot's starting node, fallback behavior, "
            "and message similarity threshold."
        )
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        # Configuration fields
        group = QGroupBox("Chatbot Settings")
        form = QFormLayout(group)
        form.setSpacing(16)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.fallback_answer = QTextEdit()
        self.fallback_answer.setMinimumHeight(85)
        self.fallback_answer.setMaximumHeight(120)
        self.fallback_answer.setPlaceholderText(
            "Enter the response used when no match is found..."
        )

        self.initial_node_id = QSpinBox()
        self.initial_node_id.setRange(1, 2147483647)

        self.fallback_node_id = QSpinBox()
        self.fallback_node_id.setRange(1, 2147483647)

        self.similarity_threshold = QDoubleSpinBox()
        self.similarity_threshold.setRange(0.0, 1.0)
        self.similarity_threshold.setDecimals(3)
        self.similarity_threshold.setSingleStep(0.05)

        form.addRow("Fallback answer:", self.fallback_answer)
        form.addRow("Initial node ID:", self.initial_node_id)
        form.addRow("Fallback node ID:", self.fallback_node_id)
        form.addRow("Similarity threshold:", self.similarity_threshold)

        root.addWidget(group)

        # Restart warning
        warning = QLabel(
            "IMPORTANT: After saving configuration changes, "
            "close and restart the application for them to take effect."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet(
self.setStyleSheet("""
    QWidget {
        background-color: #0B1120;
        color: #E5EAF3;
        font-size: 13px;
    }

    QGroupBox {
        background-color: #111827;
        border: 1px solid #263449;
        border-radius: 10px;
        margin-top: 14px;
        padding: 16px;
        font-weight: 600;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 6px;
        color: #60A5FA;
    }

    QLabel {
        color: #CBD5E1;
        background-color: transparent;
    }

    QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
        background-color: #111827;
        color: #F1F5F9;
        border: 1px solid #34445C;
        border-radius: 6px;
        padding: 8px;
        selection-background-color: #2563EB;
    }

    QLineEdit:focus, QTextEdit:focus,
    QSpinBox:focus, QDoubleSpinBox:focus {
        border: 1px solid #3B82F6;
    }

    QPushButton {
        background-color: #2563EB;
        color: white;
        border: none;
        border-radius: 7px;
        padding: 10px 18px;
        font-weight: 600;
    }

    QPushButton:hover {
        background-color: #3B82F6;
    }

    QPushButton#secondaryButton {
        background-color: #263449;
    }

    QPushButton#secondaryButton:hover {
        background-color: #34445C;
    }
""")
)
        root.addWidget(warning)

        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()

        reload_button = QPushButton("Reload from File")
        reload_button.setObjectName("secondaryButton")
        reload_button.clicked.connect(self.load_config)
        buttons.addWidget(reload_button)

        save_button = QPushButton("Save Configuration")
        save_button.clicked.connect(self.save_config)
        buttons.addWidget(save_button)

        root.addLayout(buttons)
        root.addStretch()

        self.load_config()

    def load_config(self):
        """Load settings from config.json into the form."""

        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as file:
                config = json.load(file)

            required_keys = (
                "FALLBACK_ANSWER",
                "INITIAL_NODE_ID",
                "FALLBACK_NODE_ID",
                "SIMILARITY_THRESHOLD",
            )

            missing = [
                key for key in required_keys
                if key not in config
            ]

            if missing:
                raise ValueError(
                    "Missing configuration keys: "
                    + ", ".join(missing)
                )

            if not isinstance(config["FALLBACK_ANSWER"], str):
                raise ValueError("FALLBACK_ANSWER must be a string.")

            for key in ("INITIAL_NODE_ID", "FALLBACK_NODE_ID"):
                if type(config[key]) is not int or config[key] < 1:
                    raise ValueError(
                        f"{key} must be a positive integer."
                    )

            threshold = config["SIMILARITY_THRESHOLD"]

            if (
                isinstance(threshold, bool)
                or not isinstance(threshold, (int, float))
                or not 0 <= threshold <= 1
            ):
                raise ValueError(
                    "SIMILARITY_THRESHOLD must be between 0 and 1."
                )

            self.fallback_answer.setPlainText(
                config["FALLBACK_ANSWER"]
            )
            self.initial_node_id.setValue(
                config["INITIAL_NODE_ID"]
            )
            self.fallback_node_id.setValue(
                config["FALLBACK_NODE_ID"]
            )
            self.similarity_threshold.setValue(float(threshold))

        except Exception as error:
            QMessageBox.critical(
                self,
                "Configuration Error",
                f"Could not load config.json:\n{error}",
            )

    def save_config(self):
        """Validate and save the settings to config.json."""

        fallback_answer = self.fallback_answer.toPlainText()
        initial_node_id = self.initial_node_id.value()
        fallback_node_id = self.fallback_node_id.value()
        threshold = self.similarity_threshold.value()

        if not fallback_answer.strip():
            QMessageBox.warning(
                self,
                "Invalid Configuration",
                "The fallback answer cannot be empty.",
            )
            return

        try:
            # Preserve any unrelated keys in the JSON file.
            if CONFIG_PATH.exists():
                with CONFIG_PATH.open("r", encoding="utf-8") as file:
                    config = json.load(file)
            else:
                config = {}

            config.update({
                "FALLBACK_ANSWER": fallback_answer,
                "INITIAL_NODE_ID": initial_node_id,
                "FALLBACK_NODE_ID": fallback_node_id,
                "SIMILARITY_THRESHOLD": threshold,
            })

            # Write to a temporary file first to reduce the risk
            # of leaving config.json partially written.
            temp_path = CONFIG_PATH.with_suffix(".json.tmp")

            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(config, file, indent=4, ensure_ascii=False)
                file.write("\n")

            temp_path.replace(CONFIG_PATH)

            QMessageBox.information(
                self,
                "Configuration Saved",
                "Your configuration has been saved successfully.\n\n"
                "Close and restart the application for the changes "
                "to take effect.",
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Could not save config.json:\n{error}",
            )
