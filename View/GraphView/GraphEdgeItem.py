
import math

from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import (
    QColor,
    QBrush,
    QFont,
    QFontMetricsF,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QPolygonF,
)
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsObject


class GraphEdgeItem(QGraphicsObject):
    ARROW_SIZE = 12

    def __init__(
        self,
        edge_id: int,
        source_node,
        destination_node,
        user_response: str,
        parent=None,
    ):
        super().__init__(parent)

        self.edge_id = edge_id
        self.source_node = source_node
        self.destination_node = destination_node
        self.user_response = user_response

        self.path = QPainterPath()
        self.arrow = QPolygonF()
        self.label_rect = QRectF()

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )
        self.setAcceptHoverEvents(True)
        self.setZValue(0)

        self.source_node.connected_edges.add(self)
        self.destination_node.connected_edges.add(self)

        self.update_geometry()

    def boundingRect(self):
        bounds = self.path.boundingRect().united(self.label_rect)

        if not self.arrow.isEmpty():
            bounds = bounds.united(self.arrow.boundingRect())

        return bounds.adjusted(-4, -4, 4, 4)

    def shape(self):
        stroker = QPainterPathStroker()
        stroker.setWidth(12)

        result = stroker.createStroke(self.path)

        label_path = QPainterPath()
        label_path.addRoundedRect(self.label_rect, 5, 5)
        result.addPath(label_path)

        arrow_path = QPainterPath()
        arrow_path.addPolygon(self.arrow)
        arrow_path.closeSubpath()
        result.addPath(arrow_path)

        return result

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self.isSelected():
            color = QColor("#2878D0")
            width = 2.8
        elif self.isUnderMouse():
            color = QColor("#718096")
            width = 2.2
        else:
            color = QColor("#9AA6B2")
            width = 1.6

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(
            QPen(
                color,
                width,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.drawPath(self.path)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        painter.drawPolygon(self.arrow)

        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(QPen(QColor("#D5DCE4"), 1))
        painter.drawRoundedRect(self.label_rect, 5, 5)

        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QColor("#344054"))

        painter.drawText(
            self.label_rect,
            Qt.AlignmentFlag.AlignCenter,
            self._label_text(),
        )

    def _label_text(self):
        label = self.user_response.replace("\n", " ").strip()
        return label if len(label) <= 30 else label[:27] + "..."

    def update_geometry(self):
        """Recalculate the curve, arrowhead and label."""
        if not self.source_node or not self.destination_node:
            return

        self.prepareGeometryChange()

        source_rect = self.source_node.mapRectToScene(
            self.source_node.boundingRect()
        )
        destination_rect = self.destination_node.mapRectToScene(
            self.destination_node.boundingRect()
        )

        source_center = source_rect.center()
        destination_center = destination_rect.center()

        dx = destination_center.x() - source_center.x()
        dy = destination_center.y() - source_center.y()
        distance = math.hypot(dx, dy)

        if distance < 1:
            self.path = QPainterPath()
            self.arrow = QPolygonF()
            self.label_rect = QRectF(source_center, source_center)
            self.update()
            return

        ux, uy = dx / distance, dy / distance

        # Find where the center-to-center direction intersects
        # the rectangular boundaries of the two nodes.
        def boundary_distance(rect, x_direction, y_direction):
            half_width = rect.width() / 2
            half_height = rect.height() / 2

            return min(
                half_width / max(abs(x_direction), 1e-9),
                half_height / max(abs(y_direction), 1e-9),
            )

        start_distance = boundary_distance(source_rect, ux, uy)
        end_distance = boundary_distance(
            destination_rect, ux, uy
        )

        start = QPointF(
            source_center.x() + ux * start_distance,
            source_center.y() + uy * start_distance,
        )

        tip = QPointF(
            destination_center.x() - ux * end_distance,
            destination_center.y() - uy * end_distance,
        )

        # Curve direction and bend.
        perpendicular_x = -uy
        perpendicular_y = ux
        bend = min(70.0, distance * 0.18)

        control1 = QPointF(
            start.x() + dx * 0.33 + perpendicular_x * bend,
            start.y() + dy * 0.33 + perpendicular_y * bend,
        )
        control2 = QPointF(
            tip.x() - dx * 0.33 + perpendicular_x * bend,
            tip.y() - dy * 0.33 + perpendicular_y * bend,
        )

        # Stop the visible line just before the arrowhead.
        tangent_x = tip.x() - control2.x()
        tangent_y = tip.y() - control2.y()
        tangent_length = math.hypot(tangent_x, tangent_y)

        if tangent_length < 1:
            tangent_x, tangent_y = ux, uy
            tangent_length = 1

        tx = tangent_x / tangent_length
        ty = tangent_y / tangent_length

        arrow_base = QPointF(
            tip.x() - tx * self.ARROW_SIZE,
            tip.y() - ty * self.ARROW_SIZE,
        )

        self.path = QPainterPath(start)
        self.path.cubicTo(control1, control2, arrow_base)

        px, py = -ty, tx
        half_arrow_width = self.ARROW_SIZE * 0.55

        self.arrow = QPolygonF([
            tip,
            QPointF(
                arrow_base.x() + px * half_arrow_width,
                arrow_base.y() + py * half_arrow_width,
            ),
            QPointF(
                arrow_base.x() - px * half_arrow_width,
                arrow_base.y() - py * half_arrow_width,
            ),
        ])

        # Put the response label near the center of the curve.
        midpoint = self.path.pointAtPercent(0.5)

        font = QFont()
        font.setPointSize(8)
        metrics = QFontMetricsF(font)

        label = self._label_text()
        label_width = metrics.horizontalAdvance(label) + 14
        label_height = metrics.height() + 8

        self.label_rect = QRectF(
            midpoint.x() - label_width / 2,
            midpoint.y() - label_height / 2,
            label_width,
            label_height,
        )

        self.update()

    def set_user_response(self, response: str):
        self.user_response = response
        self.update_geometry()

    def set_endpoints(self, source_node, destination_node):
        """Reconnect this edge to different visual nodes."""
        self.source_node.connected_edges.discard(self)
        self.destination_node.connected_edges.discard(self)

        self.source_node = source_node
        self.destination_node = destination_node

        self.source_node.connected_edges.add(self)
        self.destination_node.connected_edges.add(self)

        self.update_geometry()

    def detach(self):
        """Remove this edge from the nodes' connection lists."""
        self.source_node.connected_edges.discard(self)
        self.destination_node.connected_edges.discard(self)

    def set_edge_id(self, edge_id: int):
        self.edge_id = edge_id
        self.update()

    def hoverEnterEvent(self, event):
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.update()
        super().hoverLeaveEvent(event)
