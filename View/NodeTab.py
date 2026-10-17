
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QLabel,
    QMessageBox,
    QHeaderView,
    QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator

from Model.Node import Node
from Model.Edge import Edge


class NodeTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_node_id = None

        self.setup_ui()
        self.load_nodes()

    def setup_ui(self):
        self.setObjectName("NodeTab")

        self.setStyleSheet("""
            QWidget#NodeTab {
                background-color: #0f172a;
                color: #cbd5e1;
                font-family: "Segoe UI";
                font-size: 13px;
            }

            QLabel {
                color: #b8c5d9;
                background: transparent;
            }

            QLabel#PageTitle {
                color: #f1f5f9;
                font-size: 19px;
                font-weight: 700;
            }

            QLabel#PageSubtitle {
                color: #8492a8;
                font-size: 11px;
            }

            QLabel#SectionLabel {
                color: #93a4bd;
                font-size: 11px;
                font-weight: 700;
            }

            QFrame#EditorPanel {
                background-color: #111c30;
                border: 1px solid #263650;
                border-radius: 12px;
            }

            QFrame#SectionDivider {
                background-color: #243149;
                border: none;
                max-height: 1px;
            }

            QLineEdit, QTextEdit {
                background-color: #0b1425;
                color: #e5eaf5;
                border: 1px solid #2b3b54;
                border-radius: 8px;
                padding: 9px 10px;
                selection-background-color: #2563eb;
            }

            QLineEdit {
                min-height: 18px;
            }

            QLineEdit:focus, QTextEdit:focus {
                border: 1px solid #3b82f6;
                background-color: #101d33;
            }

            QLineEdit:read-only {
                background-color: #162238;
                color: #93a4bd;
                border-color: #263650;
            }

            QLineEdit::placeholder,
            QTextEdit::placeholder {
                color: #718096;
            }

            QPushButton {
                background-color: #1a263b;
                color: #cbd5e1;
                border: 1px solid #2b3b54;
                border-radius: 8px;
                padding: 9px 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #263650;
                border-color: #3b5275;
                color: #f1f5f9;
            }

            QPushButton:pressed {
                background-color: #111c30;
            }

            QPushButton#AddButton {
                background-color: #2563eb;
                color: white;
                border: 1px solid #3b82f6;
            }

            QPushButton#AddButton:hover {
                background-color: #3b82f6;
            }

            QPushButton#UpdateButton {
                background-color: #172c4b;
                color: #93c5fd;
                border: 1px solid #2c4d7b;
            }

            QPushButton#UpdateButton:hover {
                background-color: #203b61;
            }

            QPushButton#DeleteButton {
                background-color: #351d2b;
                color: #fda4af;
                border: 1px solid #6c2c43;
            }

            QPushButton#DeleteButton:hover {
                background-color: #512337;
            }

            QTableWidget {
                background-color: #0b1425;
                alternate-background-color: #101b2e;
                color: #dbe4f0;
                border: 1px solid #263650;
                border-radius: 10px;
                gridline-color: #1f2d43;
                outline: none;
                selection-background-color: #1c3b67;
                selection-color: #ffffff;
            }

            QTableWidget::item {
                padding: 8px;
                border: none;
            }

            QTableWidget::item:hover {
                background-color: #17263e;
            }

            QHeaderView::section {
                background-color: #162238;
                color: #93a4bd;
                border: none;
                border-bottom: 1px solid #34445e;
                padding: 10px 8px;
                font-weight: 700;
            }

            QTableCornerButton::section {
                background-color: #162238;
                border: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(14)

        # -------------------------------------------------
        # Page header
        # -------------------------------------------------
        header_layout = QHBoxLayout()
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        title = QLabel("Node Management")
        title.setObjectName("PageTitle")

        subtitle = QLabel(
            "Create chatbot responses and manage conversation states."
        )
        subtitle.setObjectName("PageSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # -------------------------------------------------
        # Editor panel
        # -------------------------------------------------
        editor_panel = QFrame()
        editor_panel.setObjectName("EditorPanel")

        editor_layout = QVBoxLayout(editor_panel)
        editor_layout.setContentsMargins(15, 14, 15, 15)
        editor_layout.setSpacing(12)

        section_title = QLabel("NODE CONFIGURATION")
        section_title.setObjectName("SectionLabel")
        editor_layout.addWidget(section_title)

        divider = QFrame()
        divider.setObjectName("SectionDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        editor_layout.addWidget(divider)

        # Node ID
        id_layout = QVBoxLayout()
        id_layout.setSpacing(6)

        id_label = QLabel("Node ID")

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText(
            "Leave empty to generate an ID automatically"
        )
        self.id_input.setValidator(
            QIntValidator(1, 2147483647, self)
        )
        self.id_input.setClearButtonEnabled(True)

        id_layout.addWidget(id_label)
        id_layout.addWidget(self.id_input)

        editor_layout.addLayout(id_layout)

        # Node answer
        answer_layout = QVBoxLayout()
        answer_layout.setSpacing(6)

        answer_label = QLabel("Chatbot Response")

        self.answer_input = QTextEdit()
        self.answer_input.setPlaceholderText(
            "Enter the chatbot response for this node..."
        )
        self.answer_input.setMinimumHeight(75)
        self.answer_input.setMaximumHeight(110)

        answer_layout.addWidget(answer_label)
        answer_layout.addWidget(self.answer_input)

        editor_layout.addLayout(answer_layout)

        # Actions
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.add_button = QPushButton("＋  Add Node")
        self.add_button.setObjectName("AddButton")

        self.update_button = QPushButton("Update Node")
        self.update_button.setObjectName("UpdateButton")

        self.delete_button = QPushButton("Delete Node")
        self.delete_button.setObjectName("DeleteButton")

        self.clear_button = QPushButton("Clear")
        self.refresh_button = QPushButton("Refresh")

        for button in (
            self.add_button,
            self.update_button,
            self.delete_button,
            self.clear_button,
            self.refresh_button,
        ):
            button.setCursor(Qt.CursorShape.PointingHandCursor)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.refresh_button)

        editor_layout.addLayout(button_layout)
        layout.addWidget(editor_panel)

        # -------------------------------------------------
        # Node table
        # -------------------------------------------------
        table_header = QHBoxLayout()

        table_title = QLabel("Registered Nodes")
        table_title.setStyleSheet("""
            QLabel {
                color: #e5eaf5;
                font-size: 14px;
                font-weight: 700;
            }
        """)

        self.node_count_label = QLabel("0 nodes")
        self.node_count_label.setStyleSheet("""
            QLabel {
                color: #60a5fa;
                background-color: #14233b;
                border: 1px solid #20395d;
                border-radius: 8px;
                padding: 4px 9px;
                font-size: 11px;
            }
        """)

        table_header.addWidget(table_title)
        table_header.addStretch()
        table_header.addWidget(self.node_count_label)

        layout.addLayout(table_header)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels([
            "Node ID",
            "Answer",
        ])

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )
        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(40)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch,
        )

        layout.addWidget(self.table, 1)

        # -------------------------------------------------
        # Signals
        # -------------------------------------------------
        self.add_button.clicked.connect(self.add_node)
        self.update_button.clicked.connect(self.update_node)
        self.delete_button.clicked.connect(self.delete_node)
        self.clear_button.clicked.connect(self.clear_form)
        self.refresh_button.clicked.connect(self.load_nodes)

        self.table.itemSelectionChanged.connect(
            self.select_node
        )

    # -----------------------------------------------------
    # Load nodes
    # -----------------------------------------------------
    def load_nodes(self):
        nodes = Node.get_all()

        self.table.setRowCount(0)

        for node in nodes:
            row = self.table.rowCount()
            self.table.insertRow(row)

            id_item = QTableWidgetItem(str(node.Id))
            id_item.setTextAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            answer_item = QTableWidgetItem(node.Answer)

            self.table.setItem(row, 0, id_item)
            self.table.setItem(row, 1, answer_item)

        count = len(nodes)
        self.node_count_label.setText(
            f"{count} node{'s' if count != 1 else ''}"
        )

    # -----------------------------------------------------
    # Clear editor
    # -----------------------------------------------------
    def clear_form(self):
        self.selected_node_id = None
        self.table.clearSelection()
        self.id_input.clear()
        self.answer_input.clear()
        self.id_input.setReadOnly(False)

    # -----------------------------------------------------
    # Select node
    # -----------------------------------------------------
    def select_node(self):
        row = self.table.currentRow()

        if row < 0:
            return

        self.selected_node_id = int(
            self.table.item(row, 0).text()
        )

        self.id_input.setText(str(self.selected_node_id))
        self.id_input.setReadOnly(True)

        self.answer_input.setPlainText(
            self.table.item(row, 1).text()
        )

    # -----------------------------------------------------
    # Validate answer
    # -----------------------------------------------------
    def validate_answer(self):
        answer = self.answer_input.toPlainText().strip()

        if not answer:
            QMessageBox.warning(
                self,
                "Invalid node",
                "The node answer cannot be empty.",
            )
            return None

        return answer

    # -----------------------------------------------------
    # Generate next node ID
    # -----------------------------------------------------
    def next_node_id(self):
        node_ids = [node.Id for node in Node.get_all()]
        return max(node_ids, default=0) + 1

    # -----------------------------------------------------
    # Add node
    # -----------------------------------------------------
    def add_node(self):
        answer = self.validate_answer()

        if answer is None:
            return

        try:
            raw_id = self.id_input.text().strip()
            node_id = (
                int(raw_id) if raw_id else self.next_node_id()
            )

            if Node.get(node_id) is not None:
                QMessageBox.warning(
                    self,
                    "Duplicate ID",
                    f"Node {node_id} already exists.",
                )
                return

            Node(
                Id=node_id,
                Answer=answer,
            ).save()

            self.load_nodes()
            self.clear_form()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error adding node",
                str(error),
            )

    # -----------------------------------------------------
    # Update node
    # -----------------------------------------------------
    def update_node(self):
        if self.selected_node_id is None:
            QMessageBox.information(
                self,
                "Select a node",
                "Select a node from the table first.",
            )
            return

        answer = self.validate_answer()

        if answer is None:
            return

        try:
            node = Node.get(self.selected_node_id)

            if node is None:
                QMessageBox.warning(
                    self,
                    "Node not found",
                    "The node no longer exists.",
                )
                self.load_nodes()
                self.clear_form()
                return

            node.Answer = answer
            node.save()

            self.load_nodes()
            self.clear_form()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error updating node",
                str(error),
            )

    # -----------------------------------------------------
    # Delete node
    # -----------------------------------------------------
    def delete_node(self):
        if self.selected_node_id is None:
            QMessageBox.information(
                self,
                "Select a node",
                "Select a node from the table first.",
            )
            return

        node_id = self.selected_node_id

        # Prevent deletion while edges reference this node.
        related_edges = [
            edge for edge in Edge.get_all()
            if edge.NodeFromID == node_id
            or edge.NodeToID == node_id
        ]

        if related_edges:
            QMessageBox.warning(
                self,
                "Node is in use",
                f"Node {node_id} is referenced by "
                f"{len(related_edges)} edge(s).\n\n"
                "Delete or update those edges first.",
            )
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm deletion",
            f"Delete node {node_id}?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        try:
            node = Node.get(node_id)

            if node is None:
                QMessageBox.warning(
                    self,
                    "Node not found",
                    "The node may already have been deleted.",
                )
                self.load_nodes()
                self.clear_form()
                return

            node.delete()

            self.load_nodes()
            self.clear_form()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error deleting node",
                str(error),
            )
