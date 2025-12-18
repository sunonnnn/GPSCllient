from PyQt5.QtWidgets import QListWidget, QLabel, QListWidgetItem, QVBoxLayout, QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class SensorListWidget(QWidget):
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.title = QLabel("Connected Sensors")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            padding: 10px;
        """)
        
        self.list_widget = QListWidget()
        self.list_widget.setFixedWidth(300)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 2px solid #d0d0d0;
                border-radius: 10px;
                padding: 5px;
                font-size: 16px;
            }

            QListWidget::item {
                padding: 8px;
                background-color: #f7f7f7;
                border-radius: 5px;
                margin-bottom: 5px;
            }

            QListWidget::item:selected {
                background-color: #4a90e2;
                color: white;
            }
        """)
        
        layout.addWidget(self.title)
        layout.addWidget(self.list_widget)
    
    def add_sensor(self, ip, channel):
        text = f"{ip:<18}  {channel}"
        item = QListWidgetItem(text)
        item.setFont(QFont("Courier New", 18, QFont.Bold))
        self.list_widget.addItem(item)
    
    def clear(self):
        self.list_widget.clear()
    
    def set_title(self, title):
        self.title.setText(title)
