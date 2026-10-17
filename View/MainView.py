
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QLabel,
    QMessageBox,
    QFrame,
)
from PyQt6.QtCore import Qt

from Service.Graph import Graph
from View.ConfigTab import ConfigTab
from View.NodeTab import NodeTab
from View.EdgeTab import EdgeTab
from View.ChatTab import ChatTab
from View.GraphView.GraphView import GraphView


class MainWindow(QMainWindow):
    def __init__(
        self,
        InNodeId: int = 1,
        FallBackNodeId: int = 1,
        FallBackAnswer: str = "I didn't understand. Could you rephrase that?",
        Threshold: float = 0.75,
        parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle("Graph based Chatbot")
        self.resize(1400, 850)
        self.setMinimumSize(1000, 650)

        self.graph = Graph(
            Id=1,
            InNodeId=InNodeId,
            FallBackNodeId=FallBackNodeId,
            FallBackAnswer=FallBackAnswer,
            Threshold=Threshold,
        )

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("MainCentralWidget")
        self.setCentralWidget(central_widget)

        self.setStyleSheet("""
            QMainWindow,
            QWidget#MainCentralWidget {
                background-color: #0b1120;
                color: #e5eaf5;
                font-family: "Segoe UI";
                font-size: 13px;
            }

            QLabel {
                color: #cbd5e1;
            }

            QLabel#AppTitle {
                color: #f1f5f9;
                font-size: 21px;
                font-weight: 750;
            }

            QLabel#AppSubtitle {
                color: #8492a8;
                font-size: 11px;
            }

            QLabel#Logo {
                background-color: #172c4b;
                color: #60a5fa;
                border: 1px solid #2c4d7b;
                border-radius: 12px;
                font-size: 15px;
                font-weight: 800;
            }

            QFrame#Header {
                background-color: #101a2d;
                border: 1px solid #243149;
                border-radius: 14px;
            }

            QFrame#HeaderDivider {
                background-color: #243149;
                border: none;
                max-height: 1px;
            }

            QTabWidget::pane {
                background-color: #0f172a;
                border: 1px solid #243149;
                border-radius: 10px;
                top: -1px;
            }

            QTabWidget > QWidget {
                background-color: #0f172a;
            }

            QTabBar::tab {
                background-color: #101a2d;
                color: #94a3b8;
                border: 1px solid #243149;
                border-bottom: none;
                padding: 11px 22px;
                margin-right: 5px;
                border-top-left-radius: 9px;
                border-top-right-radius: 9px;
                font-weight: 600;
            }

            QTabBar::tab:hover {
                background-color: #192840;
                color: #dbeafe;
            }

            QTabBar::tab:selected {
                background-color: #0f172a;
                color: #60a5fa;
                border-color: #31568a;
                border-bottom: 2px solid #3b82f6;
            }

            QPushButton {
                background-color: #1a263b;
                color: #cbd5e1;
                border: 1px solid #2b3b54;
                border-radius: 9px;
                padding: 9px 15px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #263650;
                color: #f1f5f9;
                border-color: #3b5275;
            }

            QPushButton:pressed {
                background-color: #111c30;
            }

            QPushButton#ApplyButton {
                background-color: #2563eb;
                color: white;
                border: 1px solid #3b82f6;
            }

            QPushButton#ApplyButton:hover {
                background-color: #3b82f6;
            }

            QPushButton#ApplyButton:pressed {
                background-color: #1d4ed8;
            }

            QStatusBar {
                background-color: #0b1120;
                color: #8492a8;
                border-top: 1px solid #243149;
                padding: 4px 8px;
            }

            QStatusBar::item {
                border: none;
            }

            QScrollBar:vertical {
                background-color: #101a2d;
                width: 10px;
                margin: 2px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background-color: #34445e;
                min-height: 25px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background-color: #4b6387;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

            QScrollBar:horizontal {
                background-color: #101a2d;
                height: 10px;
                margin: 2px;
                border-radius: 5px;
            }

            QScrollBar::handle:horizontal {
                background-color: #34445e;
                min-width: 25px;
                border-radius: 5px;
            }

            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 14, 16, 10)
        main_layout.setSpacing(14)

        # -------------------------------------------------
        # Application header
        # -------------------------------------------------
        header = QFrame()
        header.setObjectName("Header")

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 13, 16, 13)
        header_layout.setSpacing(12)

        logo = QLabel("SM")
        logo.setObjectName("Logo")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(46, 46)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(3)

        title = QLabel("Graph Based Chatbot")
        title.setObjectName("AppTitle")

        subtitle = QLabel(
            "Graph editor  /  Conversation testing  /  Node management"
        )
        subtitle.setObjectName("AppSubtitle")

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        header_layout.addWidget(logo)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Header actions
        self.apply_button = QPushButton("Apply Changes")
        self.apply_button.setObjectName("ApplyButton")
        self.apply_button.setToolTip(
            "Reload saved graph data and reset the chat"
        )

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setToolTip(
            "Refresh the editor views and chatbot graph"
        )

        self.reset_button = QPushButton("Reset Chat")
        self.reset_button.setToolTip(
            "Reset the current conversation"
        )

        header_layout.addWidget(self.apply_button)
        header_layout.addWidget(self.refresh_button)
        header_layout.addWidget(self.reset_button)

        main_layout.addWidget(header)

        # -------------------------------------------------
        # Main tabs
        # -------------------------------------------------
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMovable(False)
        self.tabs.setUsesScrollButtons(True)

        self.node_tab = NodeTab()
        self.edge_tab = EdgeTab()
        self.graph_view = GraphView()
        self.chat_tab = ChatTab(self.graph)
        self.config_tab = ConfigTab()
        self.tabs.addTab(self.chat_tab, "Chat Test")
        self.tabs.addTab(self.graph_view, "Graph")
        self.tabs.addTab(self.node_tab, "Nodes")
        self.tabs.addTab(self.edge_tab, "Edges")
        self.tabs.addTab(self.config_tab, "Configuration")


        main_layout.addWidget(self.tabs, 1)

        # -------------------------------------------------
        # Status bar
        # -------------------------------------------------
        self.statusBar().showMessage("Ready")

        # -------------------------------------------------
        # Signals
        # -------------------------------------------------
        self.apply_button.clicked.connect(self.apply_changes)
        self.refresh_button.clicked.connect(self.refresh_all)
        self.reset_button.clicked.connect(self.chat_tab.reset_chat)

    # -----------------------------------------------------
    # Apply changes
    # -----------------------------------------------------
    def apply_changes(self):
        try:
            self.graph.load()
            self.graph.reset()

            self.node_tab.load_nodes()
            self.edge_tab.refresh()
            self.graph_view.refresh_graph()

            self._reset_chat_display()

            self.statusBar().showMessage(
                "Changes applied successfully",
                5000,
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Apply Changes Failed",
                str(error),
            )

    # -----------------------------------------------------
    # Refresh all editor views
    # -----------------------------------------------------
    def refresh_all(self):
        try:
            self.node_tab.load_nodes()
            self.edge_tab.refresh()
            self.graph_view.refresh_graph()

            # Reload graph data without creating a new Graph instance.
            self.graph.load()
            self.graph.reset()

            self._reset_chat_display()

            self.statusBar().showMessage(
                "Data refreshed",
                3000,
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Refresh Failed",
                str(error),
            )

    # -----------------------------------------------------
    # Reset chat display after graph reload
    # -----------------------------------------------------
    def _reset_chat_display(self):
        self.chat_tab.chat_history.clear()

        initial_node = self.graph.get_node(
            self.graph.ActiveNodeID
        )

        if initial_node is not None:
            self.chat_tab.show_message(
                "Bot",
                initial_node.Answer,
            )

        self.chat_tab.status_label.setText("●  Graph updated")
