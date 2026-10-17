
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLineEdit,
    QComboBox,
    QLabel,
    QMessageBox,
    QHeaderView,
    QFrame,
)
from PyQt6.QtCore import Qt

from Model.Node import Node
from Model.Edge import Edge
from Service.EmbeddingService import EmbeddingService


class EdgeTab(QWidget):
    def __init__(self, parent=None, embedding_service=None):
        super().__init__(parent)

        self.embedding_service = (
            embedding_service or EmbeddingService()
        )

        self.selected_edge_id = None

        self.setup_ui()
        self.load_nodes()
        self.load_edges()

    def setup_ui(self):
        self.setObjectName("EdgeTab")

        self.setStyleSheet("""
            QWidget#EdgeTab {
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

            QLineEdit, QComboBox {
                background-color: #0b1425;
                color: #e5eaf5;
                border: 1px solid #2b3b54;
                border-radius: 8px;
                padding: 9px 10px;
                min-height: 18px;
                selection-background-color: #2563eb;
            }

            QLineEdit:focus, QComboBox:focus {
                border: 1px solid #3b82f6;
                background-color: #101d33;
            }

            QLineEdit::placeholder {
                color: #718096;
            }

            QComboBox::drop-down {
                background-color: #17263e;
                border: none;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                width: 28px;
            }

            QComboBox QAbstractItemView {
                background-color: #111c30;
                color: #e5eaf5;
                border: 1px solid #34445e;
                selection-background-color: #1d4ed8;
                selection-color: white;
                outline: none;
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
        header_layout.setSpacing(10)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)

        title = QLabel("Edge Management")
        title.setObjectName("PageTitle")

        subtitle = QLabel(
            "Define transitions between nodes and their expected responses."
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

        section_title = QLabel("TRANSITION CONFIGURATION")
        section_title.setObjectName("SectionLabel")

        editor_layout.addWidget(section_title)

        divider = QFrame()
        divider.setObjectName("SectionDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        editor_layout.addWidget(divider)

        # Source and destination
        form_layout = QHBoxLayout()
        form_layout.setSpacing(12)

        source_layout = QVBoxLayout()
        source_layout.setSpacing(6)

        source_label = QLabel("Source Node")
        self.source_combo = QComboBox()
        self.source_combo.setMinimumWidth(150)
        self.source_combo.setToolTip(
            "Node from which the transition starts"
        )

        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_combo)

        destination_layout = QVBoxLayout()
        destination_layout.setSpacing(6)

        destination_label = QLabel("Destination Node")
        self.destination_combo = QComboBox()
        self.destination_combo.setMinimumWidth(150)
        self.destination_combo.setToolTip(
            "Node reached when this transition matches"
        )

        destination_layout.addWidget(destination_label)
        destination_layout.addWidget(self.destination_combo)

        form_layout.addLayout(source_layout, 1)
        form_layout.addLayout(destination_layout, 1)

        editor_layout.addLayout(form_layout)

        # Expected response
        response_layout = QVBoxLayout()
        response_layout.setSpacing(6)

        response_label = QLabel("Expected User Response")

        self.response_input = QLineEdit()
        self.response_input.setPlaceholderText(
            "e.g. hello, good morning, how are you?"
        )
        self.response_input.setClearButtonEnabled(True)

        response_layout.addWidget(response_label)
        response_layout.addWidget(self.response_input)

        editor_layout.addLayout(response_layout)

        # Actions
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        self.add_button = QPushButton("＋  Add Edge")
        self.add_button.setObjectName("AddButton")

        self.update_button = QPushButton("Update Edge")
        self.update_button.setObjectName("UpdateButton")

        self.delete_button = QPushButton("Delete Edge")
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
        # Edge table
        # -------------------------------------------------
        table_header = QHBoxLayout()

        table_title = QLabel("Registered Edges")
        table_title.setStyleSheet("""
            QLabel {
                color: #e5eaf5;
                font-size: 14px;
                font-weight: 700;
            }
        """)

        self.edge_count_label = QLabel("0 edges")
        self.edge_count_label.setStyleSheet("""
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
        table_header.addWidget(self.edge_count_label)

        layout.addLayout(table_header)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Source Node",
            "Destination Node",
            "User Response",
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
        self.table.verticalHeader().setDefaultSectionSize(38)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        layout.addWidget(self.table, 1)

        # -------------------------------------------------
        # Signals
        # -------------------------------------------------
        self.add_button.clicked.connect(self.add_edge)
        self.update_button.clicked.connect(self.update_edge)
        self.delete_button.clicked.connect(self.delete_edge)
        self.clear_button.clicked.connect(self.clear_form)
        self.refresh_button.clicked.connect(self.refresh)

        self.table.itemSelectionChanged.connect(
            self.select_edge
        )

    # -----------------------------------------------------
    # Load nodes into combo boxes
    # -----------------------------------------------------
    def load_nodes(self):
        self.source_combo.clear()
        self.destination_combo.clear()

        nodes = Node.get_all()

        for node in nodes:
            label = f"{node.Id}: {node.Answer}"

            self.source_combo.addItem(label, node.Id)
            self.destination_combo.addItem(label, node.Id)

    # -----------------------------------------------------
    # Load edges into table
    # -----------------------------------------------------
    def load_edges(self):
        self.table.setRowCount(0)

        edges = Edge.get_all()

        for edge in edges:
            row = self.table.rowCount()
            self.table.insertRow(row)

            values = [
                edge.Id,
                edge.NodeFromID,
                edge.NodeToID,
                edge.UserResponse,
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))

                if column < 3:
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignCenter
                    )

                self.table.setItem(row, column, item)

        count = len(edges)
        self.edge_count_label.setText(
            f"{count} edge{'s' if count != 1 else ''}"
        )

    # -----------------------------------------------------
    # Refresh
    # -----------------------------------------------------
    def refresh(self):
        self.load_nodes()
        self.load_edges()
        self.clear_form()

    # -----------------------------------------------------
    # Clear editor
    # -----------------------------------------------------
    def clear_form(self):
        self.selected_edge_id = None
        self.table.clearSelection()
        self.response_input.clear()

        if self.source_combo.count():
            self.source_combo.setCurrentIndex(0)

        if self.destination_combo.count():
            self.destination_combo.setCurrentIndex(0)

    # -----------------------------------------------------
    # Select edge
    # -----------------------------------------------------
    def select_edge(self):
        row = self.table.currentRow()

        if row < 0:
            return

        self.selected_edge_id = int(
            self.table.item(row, 0).text()
        )

        source_id = int(self.table.item(row, 1).text())
        destination_id = int(self.table.item(row, 2).text())
        response = self.table.item(row, 3).text()

        self.set_combo_node(self.source_combo, source_id)
        self.set_combo_node(
            self.destination_combo,
            destination_id,
        )

        self.response_input.setText(response)

    @staticmethod
    def set_combo_node(combo, node_id):
        index = combo.findData(node_id)

        if index >= 0:
            combo.setCurrentIndex(index)

    # -----------------------------------------------------
    # Validate editor
    # -----------------------------------------------------
    def validate_form(self):
        if self.source_combo.currentIndex() < 0:
            QMessageBox.warning(
                self,
                "Invalid edge",
                "Create a source node first.",
            )
            return None

        if self.destination_combo.currentIndex() < 0:
            QMessageBox.warning(
                self,
                "Invalid edge",
                "Create a destination node first.",
            )
            return None

        response = self.response_input.text().strip()

        if not response:
            QMessageBox.warning(
                self,
                "Invalid edge",
                "User response cannot be empty.",
            )
            return None

        return (
            self.source_combo.currentData(),
            self.destination_combo.currentData(),
            response,
        )

    # -----------------------------------------------------
    # Add edge
    # -----------------------------------------------------
    def add_edge(self):
        values = self.validate_form()

        if values is None:
            return

        source_id, destination_id, response = values

        try:
            embedding = self.embedding_service.encode(response)

            edge = Edge(
                Id=Edge.next_id(),
                NodeFromID=source_id,
                NodeToID=destination_id,
                UserResponse=response,
                Embedding=embedding,
            )

            edge.save()

            self.load_edges()
            self.clear_form()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error adding edge",
                str(error),
            )

    # -----------------------------------------------------
    # Update edge
    # -----------------------------------------------------
    def update_edge(self):
        if self.selected_edge_id is None:
            QMessageBox.information(
                self,
                "Select an edge",
                "Select an edge from the table first.",
            )
            return

        values = self.validate_form()

        if values is None:
            return

        source_id, destination_id, response = values

        try:
            edge = Edge.get(self.selected_edge_id)

            if edge is None:
                QMessageBox.warning(
                    self,
                    "Edge not found",
                    "This edge no longer exists. Refresh the table.",
                )
                self.refresh()
                return

            edge.NodeFromID = source_id
            edge.NodeToID = destination_id
            edge.UserResponse = response
            edge.Embedding = self.embedding_service.encode(
                response
            )

            edge.save()

            self.load_edges()
            self.clear_form()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error updating edge",
                str(error),
            )

    # -----------------------------------------------------
    # Delete edge
    # -----------------------------------------------------
    def delete_edge(self):
        if self.selected_edge_id is None:
            QMessageBox.information(
                self,
                "Select an edge",
                "Select an edge from the table first.",
            )
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm deletion",
            f"Delete edge {self.selected_edge_id}?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        try:
            if Edge.delete_by_id(self.selected_edge_id):
                self.load_edges()
                self.clear_form()
            else:
                QMessageBox.warning(
                    self,
                    "Edge not found",
                    "The edge may already have been deleted.",
                )
                self.refresh()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Error deleting edge",
                str(error),
            )
