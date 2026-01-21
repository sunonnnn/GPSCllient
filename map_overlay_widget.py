from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor


class MapOverlayWidget(QWidget):
    sensor_add_requested = pyqtSignal(str, str)  # ip, name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rtk_status = False
        self.setAttribute(Qt.WA_NoMousePropagation, False)
        self._setup_ui()
    
    def _setup_ui(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        self.rtk_indicator = QWidget()
        self.rtk_indicator.setFixedSize(150, 40)
        self.rtk_indicator.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 230);
                border-radius: 8px;
                border: 1px solid rgba(200, 200, 200, 150);
            }
        """)
        
        rtk_layout = QHBoxLayout(self.rtk_indicator)
        rtk_layout.setContentsMargins(10, 8, 10, 8)
        
        self.rtk_dot = QLabel("●")
        self.rtk_dot.setStyleSheet("color: #ff4444; font-size: 20px;")
        
        self.rtk_label = QLabel("RTK: OFF")
        self.rtk_label.setStyleSheet("color: #333333; font-size: 14px; font-weight: bold;")
        
        rtk_layout.addWidget(self.rtk_dot)
        rtk_layout.addWidget(self.rtk_label)
        rtk_layout.addStretch()
        
        main_layout.addWidget(self.rtk_indicator)
        main_layout.addSpacing(10)
        
        self.sensor_panel = QWidget()
        self.sensor_panel.setFixedSize(280, 90)
        self.sensor_panel.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 230);
                border-radius: 8px;
                border: 1px solid rgba(200, 200, 200, 150);
            }
        """)
        
        panel_layout = QVBoxLayout(self.sensor_panel)
        panel_layout.setContentsMargins(12, 10, 12, 10)
        panel_layout.setSpacing(8)
        
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)
        
        self.input_ip = QLineEdit()
        self.input_ip.setPlaceholderText("IP Address")
        self.input_ip.setStyleSheet("""
            QLineEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #4a90e2;
            }
        """)
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("Name")
        self.input_name.setFixedWidth(100)
        self.input_name.setStyleSheet(self.input_ip.styleSheet())
        
        input_layout.addWidget(self.input_ip)
        input_layout.addWidget(self.input_name)
        
        self.btn_add = QPushButton("Add Sensor")
        self.btn_add.setFixedHeight(32)
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #5aa0f2;
            }
            QPushButton:pressed {
                background-color: #3a80d2;
            }
        """)
        
        panel_layout.addLayout(input_layout)
        panel_layout.addWidget(self.btn_add)
        
        main_layout.addWidget(self.sensor_panel)
        main_layout.addStretch()
        
        self.btn_add.clicked.connect(self._on_add_clicked)
        self.input_name.returnPressed.connect(self._on_add_clicked)
    
    def _on_add_clicked(self):
        ip = self.input_ip.text().strip()
        name = self.input_name.text().strip()
        
        if ip:
            self.sensor_add_requested.emit(ip, name)
            self.input_ip.clear()
            self.input_name.clear()
    
    def set_rtk_status(self, connected: bool):
        self.rtk_status = connected
        if connected:
            self.rtk_dot.setStyleSheet("color: #44ff44; font-size: 20px;")
            self.rtk_label.setText("RTK: ON")
        else:
            self.rtk_dot.setStyleSheet("color: #ff4444; font-size: 20px;")
            self.rtk_label.setText("RTK: OFF")


class MapWithOverlay(QWidget):
    """지도 라벨과 오버레이를 결합한 위젯"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.map_label = QLabel()
        self.map_label.setAlignment(Qt.AlignCenter)
        
        self.overlay = MapOverlayWidget(self.map_label)
        self.overlay.raise_()
        
        layout.addWidget(self.map_label)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'overlay') and hasattr(self, 'map_label'):
            self.overlay.setGeometry(self.map_label.rect())
