
from collections import defaultdict, deque
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QRubberBand,
)

from Model.Node import Node
from Model.Edge import Edge

from View.GraphView.GraphNodeItem import GraphNodeItem
from View.GraphView.GraphEdgeItem import GraphEdgeItem


class GraphCanvas(QGraphicsView):
    """
    Interactive graph canvas for chatbot nodes and edges.

    Responsibilities:
    - Load nodes and edges from the existing models.
    - Draw directed edges between nodes.
    - Arrange nodes automatically.
    - Report selection changes to the parent GraphView.
    - Support zooming, panning and node movement.
    """

    selection_changed = pyqtSignal(object)
    graph_loaded = pyqtSignal()

    NODE_WIDTH = GraphNodeItem.WIDTH
    NODE_HEIGHT = GraphNodeItem.HEIGHT

    HORIZONTAL_SPACING = 110
    VERTICAL_SPACING = 100
    node_creation_requested = pyqtSignal(object)  # Scene position
    edge_creation_requested = pyqtSignal(int, int)  # Source ID, destination ID
    mode_status_changed = pyqtSignal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mode = "select"
        self.connect_source_id = None
        self.scene_graph = QGraphicsScene(self)
        self.setScene(self.scene_graph)
        self._initial_layout_done = False
        self.node_items = {}
        self.edge_items = {}

        self._zoom = 1.0
        self._panning = False
        self._pan_position = None

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )

        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorViewCenter
        )

        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setRubberBandSelectionMode(
            Qt.ItemSelectionMode.IntersectsItemShape
        )

        self.setBackgroundBrush(QColor("#0B1120"))

        self.setMinimumSize(500, 350)

        self.scene_graph.selectionChanged.connect(
            self._on_selection_changed
        )

        self.load_graph()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    
    def load_graph(self):
        """Synchronize the canvas with the database without resetting layout."""
        nodes = Node.get_all()
        edges = Edge.get_all()

        node_records = {node.Id: node for node in nodes}
        edge_records = {edge.Id: edge for edge in edges}

        # Remove deleted edges first so they detach from their nodes.
        for edge_id in list(self.edge_items):
            if edge_id not in edge_records:
                item = self.edge_items.pop(edge_id)
                item.detach()
                self.scene_graph.removeItem(item)

        # Remove deleted nodes.
        for node_id in list(self.node_items):
            if node_id not in node_records:
                item = self.node_items.pop(node_id)
                self.scene_graph.removeItem(item)

        # Update existing nodes without changing their positions.
        for node_id, node in node_records.items():
            item = self.node_items.get(node_id)

            if item is not None:
                item.set_answer(node.Answer)
            else:
                item = GraphNodeItem(node_id, node.Answer)
                self.node_items[node_id] = item
                self.scene_graph.addItem(item)

                # Place new nodes to the right of the existing layout.
                if len(self.node_items) == 1:
                    item.setPos(0, 0)
                else:
                    right_edge = max(
                        existing.pos().x()
                        + existing.boundingRect().width()
                        for existing in self.node_items.values()
                        if existing is not item
                    )
                    item.setPos(
                        right_edge + self.HORIZONTAL_SPACING,
                        0,
                    )

        # Arrange automatically only on the first load.
        if not getattr(self, "_initial_layout_done", False):
            self._arrange_nodes(nodes, edges)
            self._initial_layout_done = True

        # Update existing edges or create new ones.
        for edge_id, edge in edge_records.items():
            source = self.node_items.get(edge.NodeFromID)
            destination = self.node_items.get(edge.NodeToID)

            # Skip invalid references rather than crashing the canvas.
            if source is None or destination is None:
                continue

            item = self.edge_items.get(edge_id)

            if item is not None:
                if (
                    item.source_node is not source
                    or item.destination_node is not destination
                ):
                    item.set_endpoints(source, destination)

                item.set_user_response(edge.UserResponse)
            else:
                item = GraphEdgeItem(
                    edge_id=edge.Id,
                    source_node=source,
                    destination_node=destination,
                    user_response=edge.UserResponse,
                )
                self.edge_items[edge_id] = item
                self.scene_graph.addItem(item)

        self._update_scene_rect()
        self.graph_loaded.emit()

    def get_node_item(self, node_id):
        """Return a visual node by its database ID."""
        return self.node_items.get(node_id)

    def get_edge_item(self, edge_id):
        """Return a visual edge by its database ID."""
        return self.edge_items.get(edge_id)

    def fit_graph(self):
        """Fit the complete graph inside the visible canvas."""
        if not self.scene_graph.items():
            return

        self.resetTransform()
        self._zoom = 1.0

        self.fitInView(
            self.scene_graph.itemsBoundingRect(),
            Qt.AspectRatioMode.KeepAspectRatio,
        )

        # fitInView changes the transformation directly.
        self._zoom = self.transform().m11()

    # ---------------------------------------------------------
    # Automatic layout
    # ---------------------------------------------------------

    def _arrange_nodes(self, nodes, edges):
        """
        Arrange nodes in layers using a breadth-first traversal.

        Nodes reachable from the first node are placed in layers.
        Disconnected nodes are placed in additional layers.
        """
        if not nodes:
            return

        node_ids = {node.Id for node in nodes}
        adjacency = defaultdict(list)

        for edge in edges:
            if (
                edge.NodeFromID in node_ids
                and edge.NodeToID in node_ids
            ):
                if edge.NodeToID not in adjacency[edge.NodeFromID]:
                    adjacency[edge.NodeFromID].append(
                        edge.NodeToID
                    )

        visited = set()
        layers = []
        remaining = sorted(node_ids)

        while remaining:
            # Start a new component with the smallest unvisited ID.
            start = remaining[0]
            queue = deque([(start, 0)])
            component_layers = defaultdict(list)
            component_visited = set()

            while queue:
                node_id, depth = queue.popleft()

                if node_id in component_visited:
                    continue

                component_visited.add(node_id)
                visited.add(node_id)
                component_layers[depth].append(node_id)

                for destination_id in adjacency[node_id]:
                    if destination_id not in component_visited:
                        queue.append(
                            (destination_id, depth + 1)
                        )

            remaining = sorted(node_ids - visited)

            for depth in sorted(component_layers):
                layers.append(component_layers[depth])

        # Place each layer horizontally and center it vertically.
        max_layer_height = max(
            len(layer) for layer in layers
        )

        for layer_index, layer in enumerate(layers):
            x = layer_index * (
                self.NODE_WIDTH + self.HORIZONTAL_SPACING
            )

            total_height = (
                len(layer) * self.NODE_HEIGHT
                + max(0, len(layer) - 1) * self.VERTICAL_SPACING
            )

            y_start = -total_height / 2

            for position, node_id in enumerate(sorted(layer)):
                y = (
                    y_start
                    + position
                    * (
                        self.NODE_HEIGHT
                        + self.VERTICAL_SPACING
                    )
                )

                item = self.node_items[node_id]
                item.setPos(x, y)

    # ---------------------------------------------------------
    # Selection
    # ---------------------------------------------------------

    def _on_selection_changed(self):
        """Send the selected node or edge to the parent widget."""
        selected = self.scene_graph.selectedItems()

        if not selected:
            self.selection_changed.emit(None)
            return

        # Prefer a node when multiple items are selected.
        selected_nodes = [
            item
            for item in selected
            if isinstance(item, GraphNodeItem)
        ]

        if selected_nodes:
            self.selection_changed.emit(selected_nodes[0])
            return

        selected_edges = [
            item
            for item in selected
            if isinstance(item, GraphEdgeItem)
        ]

        if selected_edges:
            self.selection_changed.emit(selected_edges[0])
            return

        self.selection_changed.emit(None)

    # ---------------------------------------------------------
    # Zoom
    # ---------------------------------------------------------

    def wheelEvent(self, event):
        """Zoom in or out using the mouse wheel."""
        factor = 1.15

        if event.angleDelta().y() > 0:
            zoom_factor = factor
        else:
            zoom_factor = 1 / factor

        new_zoom = self._zoom * zoom_factor

        if 0.15 <= new_zoom <= 4.0:
            self.scale(zoom_factor, zoom_factor)
            self._zoom = new_zoom

    # ---------------------------------------------------------
    # Pan
    # ---------------------------------------------------------
    def mousePressEvent(self, event):
        # Middle mouse button always pans the canvas.
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_position = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        position = event.position().toPoint()
        clicked_item = self.itemAt(position)

        # -------------------------------------------------
        # Create-node mode
        # -------------------------------------------------
        if self.mode == "create_node":
            if clicked_item is None:
                scene_position = self.mapToScene(position)
                self.node_creation_requested.emit(scene_position)

            event.accept()
            return

        # -------------------------------------------------
        # Connect-nodes mode
        # -------------------------------------------------
        if self.mode == "connect_nodes":
            if isinstance(clicked_item, GraphNodeItem):
                node_id = clicked_item.node_id

                if self.connect_source_id is None:
                    self.connect_source_id = node_id

                    self.scene_graph.clearSelection()
                    clicked_item.setSelected(True)

                    self.mode_status_changed.emit(
                        f"Source: Node {node_id}. "
                        "Now click the destination node."
                    )

                else:
                    source_id = self.connect_source_id
                    destination_id = node_id
                    self.connect_source_id = None

                    if source_id == destination_id:
                        self.mode_status_changed.emit(
                            "Choose a different destination node."
                        )
                    else:
                        self.edge_creation_requested.emit(
                            source_id,
                            destination_id,
                        )

            event.accept()
            return

        # -------------------------------------------------
        # Normal selection / node movement
        # -------------------------------------------------
        super().mousePressEvent(event)
    def mouseMoveEvent(self, event):
        if self._panning and self._pan_position is not None:
            current_position = event.position().toPoint()
            delta = current_position - self._pan_position

            self._pan_position = current_position

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )

            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self._pan_position = None

            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        super().mouseReleaseEvent(event)

    # ---------------------------------------------------------
    # Scene boundaries
    # ---------------------------------------------------------

    def _update_scene_rect(self):
        """Keep enough space around all graph items."""
        bounds = self.scene_graph.itemsBoundingRect().adjusted(
            -100,
            -100,
            100,
            100,
        )

        self.scene_graph.setSceneRect(bounds)
    def set_mode(self, mode: str):
        """Switch between select, create-node and connect-node modes."""
        if mode not in {"select", "create_node", "connect_nodes"}:
            raise ValueError(f"Unknown graph editing mode: {mode}")

        self.mode = mode
        self.connect_source_id = None

        self.scene_graph.clearSelection()

        if mode == "select":
            self.setDragMode(
                QGraphicsView.DragMode.RubberBandDrag
            )
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.mode_status_changed.emit(
                "Select mode: click to edit, drag nodes to move them."
            )

        elif mode == "create_node":
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.mode_status_changed.emit(
                "Create node: click an empty area of the canvas."
            )

        else:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.mode_status_changed.emit(
                "Connect nodes: click a source node, then a destination node."
            )