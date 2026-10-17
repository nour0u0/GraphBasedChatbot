
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextBrowser,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt

from Service.Graph import Graph


class ChatTab(QWidget):
    def __init__(self, graph: Graph, parent=None):
        super().__init__(parent)

        self.graph = graph

        self.setup_ui()

        node = self.graph.get_node(self.graph.ActiveNodeID)
        if node is not None:
            self.show_message("Bot", node.Answer)

    def setup_ui(self):
        self.setObjectName("ChatTab")

        self.setStyleSheet("""
            QWidget#ChatTab {
                background-color: #0b1120;
                color: #e5eaf5;
                font-family: "Segoe UI";
                font-size: 13px;
            }

            QLabel {
                color: #cbd5e1;
            }

            QLabel#HeaderTitle {
                color: #f1f5f9;
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#HeaderSubtitle {
                color: #8492a8;
                font-size: 11px;
            }

            QLabel#StatusLabel {
                color: #60a5fa;
                font-size: 11px;
                padding: 5px 9px;
                background-color: #14233b;
                border: 1px solid #20395d;
                border-radius: 9px;
            }

            QTextBrowser {
                background-color: #0f172a;
                color: #e5eaf5;
                border: 1px solid #243149;
                border-radius: 14px;
                padding: 12px;
                selection-background-color: #2563eb;
            }

            QLineEdit {
                background-color: #111c30;
                color: #f1f5f9;
                border: 1px solid #2a3954;
                border-radius: 12px;
                padding: 12px 14px;
                font-size: 13px;
                selection-background-color: #2563eb;
            }

            QLineEdit:focus {
                border: 1px solid #3b82f6;
                background-color: #142039;
            }

            QLineEdit::placeholder {
                color: #718096;
            }

            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 10px 17px;
                font-weight: 600;
                font-size: 12px;
            }

            QPushButton#SendButton {
                background-color: #2563eb;
                color: white;
            }

            QPushButton#SendButton:hover {
                background-color: #3b82f6;
            }

            QPushButton#SendButton:pressed {
                background-color: #1d4ed8;
            }

            QPushButton#ResetButton {
                background-color: #1a263b;
                color: #b8c5d9;
                border: 1px solid #2b3b54;
            }

            QPushButton#ResetButton:hover {
                background-color: #263650;
                color: #f1f5f9;
            }

            QFrame#HeaderDivider {
                background-color: #243149;
                border: none;
                max-height: 1px;
            }

            QFrame#ComposerFrame {
                background-color: #0b1120;
                border: none;
            }
        """)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(18, 16, 18, 16)
        root_layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        bot_icon = QLabel("AI")
        bot_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bot_icon.setFixedSize(42, 42)
        bot_icon.setStyleSheet("""
            QLabel {
                background-color: #172c4b;
                color: #60a5fa;
                border: 1px solid #2c4d7b;
                border-radius: 13px;
                font-size: 15px;
                font-weight: 800;
            }
        """)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel("Chat Assistant")
        title.setObjectName("HeaderTitle")

        subtitle = QLabel("Local graph-based chatbot")
        subtitle.setObjectName("HeaderSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addWidget(bot_icon)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        self.status_label = QLabel("●  Chatbot ready")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        header_layout.addWidget(self.status_label)
        root_layout.addLayout(header_layout)

        divider = QFrame()
        divider.setObjectName("HeaderDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        root_layout.addWidget(divider)

        # Conversation history
        self.chat_history = QTextBrowser()
        self.chat_history.setOpenExternalLinks(False)
        self.chat_history.setOpenLinks(False)
        self.chat_history.setFrameShape(QFrame.Shape.NoFrame)
        self.chat_history.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        root_layout.addWidget(self.chat_history, 1)

        # Composer
        composer_layout = QHBoxLayout()
        composer_layout.setSpacing(9)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText(
            "Write a message..."
        )
        self.message_input.setMinimumHeight(44)

        self.send_button = QPushButton("Send  ➤")
        self.send_button.setObjectName("SendButton")
        self.send_button.setMinimumHeight(44)
        self.send_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.reset_button = QPushButton("Reset")
        self.reset_button.setObjectName("ResetButton")
        self.reset_button.setMinimumHeight(44)
        self.reset_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        composer_layout.addWidget(self.message_input, 1)
        composer_layout.addWidget(self.send_button)
        composer_layout.addWidget(self.reset_button)

        root_layout.addLayout(composer_layout)

        # Existing signal connections
        self.send_button.clicked.connect(self.send_message)
        self.message_input.returnPressed.connect(
            self.send_message
        )
        self.reset_button.clicked.connect(self.reset_chat)

    def show_message(self, sender: str, message: str):
        safe_sender = self.escape_html(str(sender))
        safe_message = self.escape_html(str(message))
        safe_message = safe_message.replace("\n", "<br>")

        if sender == "You":
            alignment = "right"
            background = "#18345a"
            border = "#28518a"
            name_color = "#93c5fd"
            label = "YOU"
            side_spacing = "left"
        else:
            alignment = "left"
            background = "#182235"
            border = "#2a3952"
            name_color = "#60a5fa"
            label = "BOT"
            side_spacing = "right"

        html = f"""
        <div style="
            width: 100%;
            text-align: {alignment};
            margin-top: 9px;
            margin-bottom: 9px;
        ">
            <table
                align="{alignment}"
                cellpadding="0"
                cellspacing="0"
                style="border-collapse: collapse;"
            >
                <tr>
                    <td style="
                        background-color: {background};
                        border: 1px solid {border};
                        border-radius: 13px;
                        padding: 10px 14px;
                        color: #e5eaf5;
                        text-align: left;
                    ">
                        <div style="
                            color: {name_color};
                            font-size: 10px;
                            font-weight: bold;
                            letter-spacing: 1px;
                            margin-bottom: 6px;
                        ">{label}</div>

                        <div style="
                            color: #e5eaf5;
                            font-size: 13px;
                            line-height: 1.5;
                            white-space: normal;
                            overflow-wrap: anywhere;
                        ">{safe_message}</div>
                    </td>
                </tr>
            </table>
        </div>
        """

        self.chat_history.append(html)

        scrollbar = self.chat_history.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    @staticmethod
    def escape_html(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )

    def send_message(self):
        user_message = self.message_input.text().strip()

        if not user_message:
            return

        self.show_message("You", user_message)
        self.message_input.clear()

        try:
            response = self.graph.process(user_message)

            if response:
                self.show_message("Bot", response)
            else:
                self.show_message(
                    "Bot",
                    "The graph returned an empty response."
                )

            self.status_label.setText(
                f"●  Active node: {self.graph.ActiveNodeID}"
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Chatbot error",
                str(error),
            )

    def reset_chat(self):
        self.graph.reset()
        self.chat_history.clear()

        node = self.graph.get_node(self.graph.ActiveNodeID)

        if node is not None:
            self.show_message("Bot", node.Answer)

        self.status_label.setText("●  Chatbot reset")
        self.message_input.setFocus()

    def reload_graph(self):
        """Refresh the graph after the editor applies changes."""
        try:
            self.graph.load()
            self.graph.reset()
            self.chat_history.clear()

            node = self.graph.get_node(self.graph.ActiveNodeID)

            if node is not None:
                self.show_message("Bot", node.Answer)

            self.status_label.setText("●  Graph reloaded")

        except Exception as error:
            QMessageBox.critical(
                self,
                "Graph reload error",
                str(error),
            )
