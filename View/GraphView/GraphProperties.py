
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QGroupBox,
    QMessageBox,
    QStackedWidget,
    QFrame,
)


class GraphProperties(QWidget):
    """
    Properties editor for a selected graph node or edge.

    This widget does not modify the database directly.
    It emits signals so GraphView can perform and validate changes.
    """

    save_node_requested = pyqtSignal(int, str)
    delete_node_requested = pyqtSignal(int)

    save_edge_requested = pyqtSignal(int, int, int, str)
    delete_edge_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_item = None
        self.selected_type = None

        self.setObjectName("GraphProperties")
        self.setMinimumWidth(260)

        self._build_ui()
        self._apply_style()
        self.clear_selection()

    # ---------------------------------------------------------
    # Styling
    # ---------------------------------------------------------

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#GraphProperties {
                background-color: #111827;
                color: #E5E7EB;
            }

            QLabel {
                color: #CBD5E1;
                font-size: 12px;
            }

            QLabel#PropertiesTitle {
                color: #F8FAFC;
                font-size: 17px;
                font-weight: 700;
                padding: 2px 0 8px 0;
            }

            QLabel#PropertiesSubtitle {
                color: #94A3B8;
                font-size: 11px;
            }

            QLabel#EmptyIcon {
                color: #60A5FA;
                font-size: 30px;
                font-weight: 600;
            }

            QLabel#EmptyTitle {
                color: #E2E8F0;
                font-size: 14px;
                font-weight: 600;
            }

            QLabel#EmptyDescription {
                color: #94A3B8;
                font-size: 12px;
            }

            QFrame#HeaderLine {
                background-color: #263449;
                border: none;
                max-height: 1px;
                min-height: 1px;
            }

            QGroupBox {
                background-color: #172234;
                border: 1px solid #2B3A50;
                border-radius: 9px;
                margin-top: 13px;
                padding: 16px 10px 10px 10px;
                font-size: 12px;
                font-weight: 600;
                color: #93C5FD;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 5px;
                color: #60A5FA;
            }

            QLineEdit, QTextEdit {
                background-color: #0B1220;
                color: #F1F5F9;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 7px;
                selection-background-color: #2563EB;
                selection-color: white;
            }

            QLineEdit {
                min-height: 20px;
            }

            QTextEdit {
                padding: 8px;
            }

            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #3B82F6;
            }

            QLineEdit:read-only {
                background-color: #1E293B;
                color: #94A3B8;
                border-color: #2B3A50;
            }

            QPushButton {
                background-color: #253247;
                color: #E2E8F0;
                border: 1px solid #36465E;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 600;
                min-height: 20px;
            }

            QPushButton:hover {
                background-color: #33465F;
                border-color: #4B6280;
            }

            QPushButton:pressed {
                background-color: #1E293B;
            }

            QPushButton#SaveButton {
                background-color: #2563EB;
                border: 1px solid #3B82F6;
                color: white;
            }

            QPushButton#SaveButton:hover {
                background-color: #1D4ED8;
            }

            QPushButton#SaveButton:pressed {
                background-color: #1E40AF;
            }

            QPushButton#DeleteButton {
                background-color: #3A202B;
                border: 1px solid #713444;
                color: #FCA5A5;
            }

            QPushButton#DeleteButton:hover {
                background-color: #512633;
                border-color: #9F4055;
            }

            QPushButton#DeleteButton:pressed {
                background-color: #321923;
            }

            QStackedWidget {
                background-color: transparent;
                border: none;
            }
        """)

    # ---------------------------------------------------------
    # UI construction
    # ---------------------------------------------------------

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(3)

        self.title_label = QLabel("Graph Properties")
        self.title_label.setObjectName("PropertiesTitle")

        self.subtitle_label = QLabel(
            "Inspect and edit the selected element"
        )
        self.subtitle_label.setObjectName("PropertiesSubtitle")

        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.subtitle_label)

        main_layout.addLayout(header_layout)

        separator = QFrame()
        separator.setObjectName("HeaderLine")
        main_layout.addWidget(separator)

        # Pages
        self.pages = QStackedWidget()

        self.empty_page = self._build_empty_page()
        self.node_page = self._build_node_page()
        self.edge_page = self._build_edge_page()

        self.pages.addWidget(self.empty_page)
        self.pages.addWidget(self.node_page)
        self.pages.addWidget(self.edge_page)

        main_layout.addWidget(self.pages, 1)

    def _build_empty_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(8, 30, 8, 20)
        layout.setSpacing(10)

        layout.addStretch()

        icon_label = QLabel("◇")
        icon_label.setObjectName("EmptyIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        title = QLabel("Nothing selected")
        title.setObjectName("EmptyTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        message = QLabel(
            "Select a node or edge on the graph canvas "
            "to inspect its properties."
        )
        message.setObjectName("EmptyDescription")
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)

        layout.addStretch()
        return page

    def _build_node_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(10)

        group = QGroupBox("Node Configuration")
        form = QFormLayout(group)
        form.setContentsMargins(12, 18, 12, 12)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.node_id_field = QLineEdit()
        self.node_id_field.setReadOnly(True)
        self.node_id_field.setPlaceholderText("Node ID")

        self.node_answer_field = QTextEdit()
        self.node_answer_field.setPlaceholderText(
            "Enter the chatbot response for this node..."
        )
        self.node_answer_field.setMinimumHeight(140)

        form.addRow("Node ID", self.node_id_field)
        form.addRow("Answer", self.node_answer_field)

        layout.addWidget(group)

        hint = QLabel(
            "The answer is returned when the chatbot reaches this node."
        )
        hint.setObjectName("PropertiesSubtitle")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addSpacing(4)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)

        self.save_node_button = QPushButton("Save Changes")
        self.save_node_button.setObjectName("SaveButton")

        self.delete_node_button = QPushButton("Delete Node")
        self.delete_node_button.setObjectName("DeleteButton")

        self.save_node_button.clicked.connect(
            self._request_save_node
        )
        self.delete_node_button.clicked.connect(
            self._request_delete_node
        )

        buttons.addWidget(self.save_node_button, 3)
        buttons.addWidget(self.delete_node_button, 2)

        layout.addLayout(buttons)
        layout.addStretch()

        return page

    def _build_edge_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(10)

        group = QGroupBox("Edge Configuration")
        form = QFormLayout(group)
        form.setContentsMargins(12, 18, 12, 12)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.edge_id_field = QLineEdit()
        self.edge_id_field.setReadOnly(True)
        self.edge_id_field.setPlaceholderText("Edge ID")

        self.edge_source_field = QLineEdit()
        self.edge_source_field.setPlaceholderText("Source node ID")

        self.edge_destination_field = QLineEdit()
        self.edge_destination_field.setPlaceholderText(
            "Destination node ID"
        )

        self.edge_response_field = QTextEdit()
        self.edge_response_field.setPlaceholderText(
            "Enter the expected user response..."
        )
        self.edge_response_field.setMinimumHeight(120)

        form.addRow("Edge ID", self.edge_id_field)
        form.addRow("Source ID", self.edge_source_field)
        form.addRow("Destination ID", self.edge_destination_field)
        form.addRow("Expected response", self.edge_response_field)

        layout.addWidget(group)

        hint = QLabel(
            "The expected response is compared with the user's message "
            "to determine the next node."
        )
        hint.setObjectName("PropertiesSubtitle")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addSpacing(4)

        buttons = QHBoxLayout()
        buttons.setSpacing(8)

        self.save_edge_button = QPushButton("Save Changes")
        self.save_edge_button.setObjectName("SaveButton")

        self.delete_edge_button = QPushButton("Delete Edge")
        self.delete_edge_button.setObjectName("DeleteButton")

        self.save_edge_button.clicked.connect(
            self._request_save_edge
        )
        self.delete_edge_button.clicked.connect(
            self._request_delete_edge
        )

        buttons.addWidget(self.save_edge_button, 3)
        buttons.addWidget(self.delete_edge_button, 2)

        layout.addLayout(buttons)
        layout.addStretch()

        return page

    # ---------------------------------------------------------
    # Selection
    # ---------------------------------------------------------

    def show_node(self, node_item):
        """Display a selected GraphNodeItem."""
        self.selected_item = node_item
        self.selected_type = "node"

        self.title_label.setText(f"Node {node_item.node_id}")
        self.subtitle_label.setText("Node properties and response")

        self.node_id_field.setText(str(node_item.node_id))
        self.node_answer_field.setPlainText(node_item.answer)

        self.pages.setCurrentWidget(self.node_page)

    def show_edge(self, edge_item):
        """Display a selected GraphEdgeItem."""
        self.selected_item = edge_item
        self.selected_type = "edge"

        self.title_label.setText(f"Edge {edge_item.edge_id}")
        self.subtitle_label.setText("Transition and matching response")

        self.edge_id_field.setText(str(edge_item.edge_id))
        self.edge_source_field.setText(
            str(edge_item.source_node.node_id)
        )
        self.edge_destination_field.setText(
            str(edge_item.destination_node.node_id)
        )
        self.edge_response_field.setPlainText(
            edge_item.user_response
        )

        self.pages.setCurrentWidget(self.edge_page)

    def clear_selection(self):
        """Clear the editor when nothing is selected."""
        self.selected_item = None
        self.selected_type = None

        self.title_label.setText("Graph Properties")
        self.subtitle_label.setText(
            "Inspect and edit the selected element"
        )

        self.pages.setCurrentWidget(self.empty_page)

    # ---------------------------------------------------------
    # Node actions
    # ---------------------------------------------------------

    def _request_save_node(self):
        if self.selected_type != "node":
            return

        answer = self.node_answer_field.toPlainText().strip()

        if not answer:
            QMessageBox.warning(
                self,
                "Invalid Node",
                "The node answer cannot be empty.",
            )
            return

        node_id = self.selected_item.node_id
        self.save_node_requested.emit(node_id, answer)

    def _request_delete_node(self):
        if self.selected_type != "node":
            return

        node_id = self.selected_item.node_id

        result = QMessageBox.question(
            self,
            "Delete Node",
            (
                f"Delete node {node_id}?\n\n"
                "All edges entering or leaving this node "
                "will also be deleted."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if result == QMessageBox.StandardButton.Yes:
            self.delete_node_requested.emit(node_id)

    # ---------------------------------------------------------
    # Edge actions
    # ---------------------------------------------------------

    def _request_save_edge(self):
        if self.selected_type != "edge":
            return

        try:
            source_id = int(
                self.edge_source_field.text().strip()
            )
            destination_id = int(
                self.edge_destination_field.text().strip()
            )
        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Edge",
                "Source and destination IDs must be integers.",
            )
            return

        response = self.edge_response_field.toPlainText().strip()

        if not response:
            QMessageBox.warning(
                self,
                "Invalid Edge",
                "The expected response cannot be empty.",
            )
            return

        edge_id = self.selected_item.edge_id

        self.save_edge_requested.emit(
            edge_id,
            source_id,
            destination_id,
            response,
        )

    def _request_delete_edge(self):
        if self.selected_type != "edge":
            return

        edge_id = self.selected_item.edge_id

        result = QMessageBox.question(
            self,
            "Delete Edge",
            f"Delete edge {edge_id}?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if result == QMessageBox.StandardButton.Yes:
            self.delete_edge_requested.emit(edge_id)
