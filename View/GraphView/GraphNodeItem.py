
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsObject


class GraphNodeItem(QGraphicsObject):
    WIDTH = 180
    HEIGHT = 76
    CORNER_RADIUS = 12

    def __init__(self, node_id: int, answer: str, parent=None):
        super().__init__(parent)

        self.node_id = node_id
        self.answer = answer
        self.connected_edges = set()

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setZValue(1)

    def boundingRect(self):
        return QRectF(0, 0, self.WIDTH, self.HEIGHT)

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.isSelected():
            fill, border, width = "#DCEBFF", "#2878D0", 2.5
        elif self.isUnderMouse():
            fill, border, width = "#F0F5FC", "#789BC5", 1.8
        else:
            fill, border, width = "#FFFFFF", "#AAB4C0", 1.2

        painter.setBrush(QBrush(QColor(fill)))
        painter.setPen(QPen(QColor(border), width))
        painter.drawRoundedRect(
            self.boundingRect(),
            self.CORNER_RADIUS,
            self.CORNER_RADIUS,
        )

        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QColor("#1D3557"))
        painter.drawText(
            QRectF(10, 7, self.WIDTH - 20, 20),
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter,
            f"Node {self.node_id}",
        )

        font.setBold(False)
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(QColor("#465568"))

        preview = self.answer.replace("\n", " ").strip()
        if len(preview) > 45:
            preview = preview[:42] + "..."

        painter.drawText(
            QRectF(10, 30, self.WIDTH - 20, self.HEIGHT - 36),
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop,
            preview,
        )

    def itemChange(self, change, value):
        result = super().itemChange(change, value)

        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            for edge in tuple(self.connected_edges):
                edge.update_geometry()

        return result

    def set_answer(self, answer: str):
        self.answer = answer
        self.update()

    def set_node_id(self, node_id: int):
        self.node_id = node_id
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def hoverEnterEvent(self, event):
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.update()
        super().hoverLeaveEvent(event)
