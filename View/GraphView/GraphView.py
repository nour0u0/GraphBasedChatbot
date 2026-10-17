
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QPushButton,
    QButtonGroup,
    QLabel,
    QMessageBox,
    QInputDialog,
    QFrame,
)

from Model.Node import Node
from Model.Edge import Edge
from Service.EmbeddingService import EmbeddingService

from View.GraphView.GraphCanvas import GraphCanvas
from View.GraphView.GraphProperties import GraphProperties
from View.GraphView.GraphNodeItem import GraphNodeItem
from View.GraphView.GraphEdgeItem import GraphEdgeItem


class GraphView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("GraphView")

        self.embedding_service = EmbeddingService()

        self._build_ui()
        self._apply_style()
        self._connect_signals()

        self.refresh_graph()

    # -------------------------------------------------
    # UI
    # -------------------------------------------------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        self.header_title = QLabel("Graph Editor")
        self.header_title.setObjectName("HeaderTitle")

        self.header_subtitle = QLabel(
            "Design and manage chatbot conversation flows"
        )
        self.header_subtitle.setObjectName("HeaderSubtitle")

        title_layout.addWidget(self.header_title)
        title_layout.addWidget(self.header_subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        self.refresh_button = QPushButton("Refresh Graph")
        self.refresh_button.setObjectName("RefreshButton")
        self.refresh_button.setToolTip(
            "Reload nodes and edges from the database"
        )
        self.refresh_button.clicked.connect(self.refresh_graph)

        header_layout.addWidget(self.refresh_button)
        layout.addLayout(header_layout)

        # Editing toolbar
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("ToolbarFrame")

        toolbar = QHBoxLayout(toolbar_frame)
        toolbar.setContentsMargins(10, 8, 10, 8)
        toolbar.setSpacing(8)

        self.tools_label = QLabel("EDITING MODE")
        self.tools_label.setObjectName("SectionLabel")
        toolbar.addWidget(self.tools_label)

        self.mode_group = QButtonGroup(self)
        self.mode_group.setExclusive(True)

        self.select_button = QPushButton("Select / Edit")
        self.select_button.setObjectName("SelectModeButton")

        self.create_node_button = QPushButton("+  Create Node")
        self.create_node_button.setObjectName("CreateModeButton")

        self.connect_nodes_button = QPushButton(
            "Connect Nodes"
        )
        self.connect_nodes_button.setObjectName(
            "ConnectModeButton"
        )

        for button in (
            self.select_button,
            self.create_node_button,
            self.connect_nodes_button,
        ):
            button.setCheckable(True)
            button.setMinimumHeight(34)
            self.mode_group.addButton(button)
            toolbar.addWidget(button)

        self.select_button.setChecked(True)
        toolbar.addStretch()

        layout.addWidget(toolbar_frame)

        # Main editor
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setObjectName("GraphSplitter")
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(5)

        self.canvas = GraphCanvas()
        self.canvas.setObjectName("GraphCanvas")

        self.properties = GraphProperties()
        self.properties.setObjectName("GraphPropertiesPanel")

        self.splitter.addWidget(self.canvas)
        self.splitter.addWidget(self.properties)

        self.splitter.setStretchFactor(0, 4)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([800, 300])

        layout.addWidget(self.splitter, 1)

        # Status bar
        status_frame = QFrame()
        status_frame.setObjectName("StatusFrame")

        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 7, 10, 7)
        status_layout.setSpacing(8)

        self.status_indicator = QLabel("●")
        self.status_indicator.setObjectName("StatusIndicator")

        self.status_label = QLabel(
            "Select mode: click an element to edit it, "
            "or drag nodes to reposition them."
        )
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setWordWrap(True)

        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_label, 1)

        layout.addWidget(status_frame)

    # -------------------------------------------------
    # Styling
    # -------------------------------------------------

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#GraphView {
                background-color: #0B1120;
                color: #E5E7EB;
            }

            QLabel {
                color: #CBD5E1;
                background: transparent;
            }

            QLabel#HeaderTitle {
                color: #F8FAFC;
                font-size: 20px;
                font-weight: 700;
            }

            QLabel#HeaderSubtitle {
                color: #94A3B8;
                font-size: 11px;
            }

            QFrame#ToolbarFrame {
                background-color: #111B2D;
                border: 1px solid #263449;
                border-radius: 8px;
            }

            QLabel#SectionLabel {
                color: #94A3B8;
                font-size: 10px;
                font-weight: 700;
                padding-right: 6px;
            }

            QPushButton {
                background-color: #1E293B;
                color: #CBD5E1;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 7px 12px;
                font-size: 11px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #2A3A52;
                border-color: #475569;
                color: #F8FAFC;
            }

            QPushButton:pressed {
                background-color: #172235;
            }

            QPushButton:checked {
                background-color: #1D4ED8;
                border: 1px solid #3B82F6;
                color: white;
            }

            QPushButton#CreateModeButton:checked {
                background-color: #075985;
                border-color: #0EA5E9;
                color: #E0F2FE;
            }

            QPushButton#ConnectModeButton:checked {
                background-color: #5B21B6;
                border-color: #8B5CF6;
                color: #F5F3FF;
            }

            QPushButton#RefreshButton {
                background-color: #172A45;
                color: #93C5FD;
                border: 1px solid #2C4B73;
                padding: 8px 12px;
            }

            QPushButton#RefreshButton:hover {
                background-color: #1E3A5F;
                border-color: #3B82F6;
            }

            QSplitter#GraphSplitter::handle {
                background-color: #263449;
                border-radius: 2px;
            }

            QSplitter#GraphSplitter::handle:hover {
                background-color: #3B82F6;
            }

            QFrame#StatusFrame {
                background-color: #111B2D;
                border: 1px solid #263449;
                border-radius: 6px;
            }

            QLabel#StatusIndicator {
                color: #60A5FA;
                font-size: 10px;
            }

            QLabel#StatusLabel {
                color: #94A3B8;
                font-size: 11px;
            }
        """)

    # -------------------------------------------------
    # Signals
    # -------------------------------------------------

    def _connect_signals(self):
        self.select_button.clicked.connect(
            lambda: self.canvas.set_mode("select")
        )
        self.create_node_button.clicked.connect(
            lambda: self.canvas.set_mode("create_node")
        )
        self.connect_nodes_button.clicked.connect(
            lambda: self.canvas.set_mode("connect_nodes")
        )

        self.canvas.selection_changed.connect(
            self._on_selection_changed
        )
        self.canvas.node_creation_requested.connect(
            self.create_node
        )
        self.canvas.edge_creation_requested.connect(
            self.create_edge
        )
        self.canvas.mode_status_changed.connect(
            self._set_status
        )

        self.properties.save_node_requested.connect(
            self.save_node
        )
        self.properties.delete_node_requested.connect(
            self.delete_node
        )
        self.properties.save_edge_requested.connect(
            self.save_edge
        )
        self.properties.delete_edge_requested.connect(
            self.delete_edge
        )

    # -------------------------------------------------
    # Status
    # -------------------------------------------------

    def _set_status(self, message: str):
        self.status_label.setText(message)

    # -------------------------------------------------
    # Selection
    # -------------------------------------------------

    def _on_selection_changed(self, item):
        if item is None:
            self.properties.clear_selection()
        elif isinstance(item, GraphNodeItem):
            self.properties.show_node(item)
        elif isinstance(item, GraphEdgeItem):
            self.properties.show_edge(item)

    # -------------------------------------------------
    # Refresh
    # -------------------------------------------------

    def refresh_graph(self):
        try:
            self.canvas.load_graph()
            self.properties.clear_selection()
            self._set_status("Graph synchronized with the database.")
        except Exception as error:
            self._show_error("Graph Refresh Failed", error)

    # -------------------------------------------------
    # Create node
    # -------------------------------------------------

    def create_node(self, position):
        answer, accepted = QInputDialog.getMultiLineText(
            self,
            "Create Node",
            "Enter the chatbot answer for this node:",
            "New chatbot response",
        )

        if not accepted:
            return

        answer = answer.strip()

        if not answer:
            self._show_error(
                "Invalid Node",
                "The node answer cannot be empty.",
            )
            return

        try:
            existing_nodes = Node.get_all()

            new_id = max(
                (node.Id for node in existing_nodes),
                default=0,
            ) + 1

            node = Node(
                Id=new_id,
                Answer=answer,
            )
            node.save()

            # Synchronize without rebuilding existing items.
            self.canvas.load_graph()

            # Place the node where the user clicked.
            node_item = self.canvas.get_node_item(new_id)

            if node_item is not None:
                node_item.setPos(position)
                self.canvas._update_scene_rect()

                self.canvas.scene_graph.clearSelection()
                node_item.setSelected(True)

            self._set_status(f"Created Node {new_id}.")

        except Exception as error:
            self._show_error("Create Node Failed", error)

    # -------------------------------------------------
    # Create edge
    # -------------------------------------------------

    def create_edge(self, source_id: int, destination_id: int):
        response, accepted = QInputDialog.getText(
            self,
            "Create Edge",
            (
                f"Expected user response for "
                f"Node {source_id} → Node {destination_id}:"
            ),
        )

        if not accepted:
            return

        response = response.strip()

        if not response:
            self._show_error(
                "Invalid Edge",
                "The expected response cannot be empty.",
            )
            return

        try:
            if Node.get(source_id) is None:
                raise ValueError(
                    f"Source node {source_id} does not exist."
                )

            if Node.get(destination_id) is None:
                raise ValueError(
                    f"Destination node {destination_id} does not exist."
                )

            embedding = self.embedding_service.encode(response)

            edge = Edge(
                Id=Edge.next_id(),
                NodeFromID=source_id,
                NodeToID=destination_id,
                UserResponse=response,
                Embedding=embedding,
            )
            edge.save()

            self.canvas.load_graph()

            edge_item = self.canvas.get_edge_item(edge.Id)
            if edge_item is not None:
                self.canvas.scene_graph.clearSelection()
                edge_item.setSelected(True)

            self._set_status(
                f"Created Edge {edge.Id}: "
                f"{source_id} → {destination_id}."
            )

        except Exception as error:
            self._show_error("Create Edge Failed", error)

    # -------------------------------------------------
    # Update node
    # -------------------------------------------------

    def save_node(self, node_id: int, answer: str):
        try:
            node = Node.get(node_id)

            if node is None:
                raise ValueError(
                    f"Node {node_id} does not exist."
                )

            answer = answer.strip()
            if not answer:
                raise ValueError(
                    "The node answer cannot be empty."
                )

            node.Answer = answer
            node.save()

            self.canvas.load_graph()
            self.properties.clear_selection()

            self._set_status(f"Updated Node {node_id}.")

        except Exception as error:
            self._show_error("Save Node Failed", error)

    # -------------------------------------------------
    # Delete node and connected edges
    # -------------------------------------------------

    def delete_node(self, node_id: int):
        try:
            node = Node.get(node_id)

            if node is None:
                raise ValueError(
                    f"Node {node_id} does not exist."
                )

            connected_edges = [
                edge
                for edge in Edge.get_all()
                if (
                    edge.NodeFromID == node_id
                    or edge.NodeToID == node_id
                )
            ]

            for edge in connected_edges:
                Edge.delete_by_id(edge.Id)

            node.delete()

            self.canvas.load_graph()
            self.properties.clear_selection()

            self._set_status(
                f"Deleted Node {node_id} and "
                f"{len(connected_edges)} connected edge(s)."
            )

        except Exception as error:
            self._show_error("Delete Node Failed", error)

    # -------------------------------------------------
    # Update edge
    # -------------------------------------------------

    def save_edge(
        self,
        edge_id: int,
        source_id: int,
        destination_id: int,
        response: str,
    ):
        try:
            edge = Edge.get(edge_id)

            if edge is None:
                raise ValueError(
                    f"Edge {edge_id} does not exist."
                )

            if Node.get(source_id) is None:
                raise ValueError(
                    f"Source node {source_id} does not exist."
                )

            if Node.get(destination_id) is None:
                raise ValueError(
                    f"Destination node {destination_id} does not exist."
                )

            response = response.strip()
            if not response:
                raise ValueError(
                    "The expected response cannot be empty."
                )

            if response != edge.UserResponse:
                edge.Embedding = self.embedding_service.encode(
                    response
                )

            edge.NodeFromID = source_id
            edge.NodeToID = destination_id
            edge.UserResponse = response
            edge.save()

            self.canvas.load_graph()
            self.properties.clear_selection()

            self._set_status(f"Updated Edge {edge_id}.")

        except Exception as error:
            self._show_error("Save Edge Failed", error)

    # -------------------------------------------------
    # Delete edge
    # -------------------------------------------------

    def delete_edge(self, edge_id: int):
        try:
            edge = Edge.get(edge_id)

            if edge is None:
                raise ValueError(
                    f"Edge {edge_id} does not exist."
                )

            Edge.delete_by_id(edge_id)

            self.canvas.load_graph()
            self.properties.clear_selection()

            self._set_status(f"Deleted Edge {edge_id}.")

        except Exception as error:
            self._show_error("Delete Edge Failed", error)

    # -------------------------------------------------
    # Errors
    # -------------------------------------------------

    def _show_error(self, title: str, error):
        QMessageBox.critical(
            self,
            title,
            str(error),
        )
