from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QColor, QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QSize

class SensorTreeItem(QWidget):
    delete_requested = pyqtSignal(str)
    
    def __init__(self, ip, parent=None):
        super().__init__(parent)
        self.ip = ip
        self.icon_path = "./icons/minus_circle_red.svg"
        self._setup_ui()
        
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
    
        self.label = QLabel(f"IP: {self.ip}")
        self.label.setFont(QFont("Courier New", 14, QFont.Bold))
        
        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(QIcon(self.icon_path))
        self.delete_btn.setIconSize(QSize(18, 18))
        self.delete_btn.setFixedSize(22, 22)
        self.delete_btn.setStyleSheet("""
        QPushButton {
            border: none;
            background: transparent;
        }
        QPushButton:hover {
            background-color: rgba(0, 0, 0, 0.08);
            border-radius: 4px;
        }
        """)
        
        self.delete_btn.clicked.connect(lambda: self.delete_requested.emit(self.ip))
        
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.delete_btn)
        
        self.delete_btn.hide()
        
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

class SensorListWidget(QWidget):
    
    sensor_deleted = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.sensor_items = {}  # {ip: {"parent": item, "widget": widget, "state": item, "gps": item}}
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
        
        self.tree_widget = QTreeWidget()
        self.tree_widget.setFixedWidth(300)
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setIndentation(20)
        self.tree_widget.itemExpanded.connect(self.on_item_expanded)
        self.tree_widget.itemCollapsed.connect(self.on_item_collapsed)

        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                background-color: #ffffff;
                border: 2px solid #d0d0d0;
                border-radius: 10px;
                padding: 5px;
                font-size: 16px;
            }

            QTreeWidget::item {
                padding: 8px;
                background-color: #f7f7f7;
                border-radius: 5px;
                margin-bottom: 2px;
                color: #333333;
            }

            QTreeWidget::item:selected {
                background-color: #4a90e2;
                color: white;
            }
        """)
        
        layout.addWidget(self.title)
        layout.addWidget(self.tree_widget)

    def on_item_expanded(self, item):
        widget = self.tree_widget.itemWidget(item, 0)
        if isinstance(widget, SensorTreeItem):
            widget.delete_btn.show()

    def on_item_collapsed(self, item):
        widget = self.tree_widget.itemWidget(item, 0)
        if isinstance(widget, SensorTreeItem):
            widget.delete_btn.hide()
    
    def add_sensor(self, ip, channel):
        if ip in self.sensor_items:
            return
        
        parent = QTreeWidgetItem(self.tree_widget)
        
        sensor_widget = SensorTreeItem(ip)
        sensor_widget.delete_requested.connect(self._on_delete_clicked)
        
        self.tree_widget.setItemWidget(parent, 0, sensor_widget)
        
        child_channel = QTreeWidgetItem(parent)
        child_channel.setText(0, f"Channel: {channel}")
        child_channel.setFont(0, QFont("Courier New", 12))
        
        child_state = QTreeWidgetItem(parent)
        child_state.setText(0, "State: Disconnected")
        child_state.setFont(0, QFont("Courier New", 12))
        child_state.setForeground(0, QColor(150, 150, 150))
        
        child_gps = QTreeWidgetItem(parent)
        child_gps.setText(0, "GPS: Not available")
        child_gps.setFont(0, QFont("Courier New", 12))
        child_gps.setForeground(0, QColor(150, 150, 150))
        
        parent.setExpanded(True)
        
        self.sensor_items[ip] = {
            "parent": parent,
            "widget": sensor_widget,
            "channel": child_channel,
            "state": child_state,
            "gps": child_gps
        }
    
    def _on_delete_clicked(self, ip):
        if ip not in self.sensor_items:
            return
        
        parent = self.sensor_items[ip]["parent"]
        index = self.tree_widget.indexOfTopLevelItem(parent)
        self.tree_widget.takeTopLevelItem(index)
        
        del self.sensor_items[ip]
        
        self.sensor_deleted.emit(ip)
    
    def update_power_status(self, ip, power_on):
        if ip not in self.sensor_items:
            return
        
        state_item = self.sensor_items[ip]["state"]
        
        if power_on is None:
            state_item.setText(0, "State: Disconnected")
            state_item.setForeground(0, QColor(150, 150, 150))
        elif power_on:
            state_item.setText(0, "State: Detected")
            state_item.setForeground(0, QColor(0, 180, 0))
        else:
            state_item.setText(0, "State: Not detected")
            state_item.setForeground(0, QColor(200, 0, 0))
    
    def update_gps(self, ip, lng, lat):
        if ip not in self.sensor_items:
            return
        
        gps_item = self.sensor_items[ip]["gps"]
        gps_item.setText(0, f"GPS: {lat:.6f},\n     {lng:.6f}")
        gps_item.setForeground(0, QColor(0, 100, 200))  # 파랑
        self.tree_widget.resizeColumnToContents(0)
    
    def clear(self):
        self.tree_widget.clear()
        self.sensor_items.clear()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    window = SensorListWidget()
    
    window.add_sensor("192.168.0.10", "CH-01")
    window.add_sensor("192.168.0.22", "CH-05")
    
    window.update_power_status("192.168.0.10", True)
    window.update_gps("192.168.0.10", 126.714391, 37.337489)
    
    window.update_power_status("192.168.0.22", False) 
    window.update_gps("192.168.0.22", 126.713423, 37.337056)
    
    window.sensor_deleted.connect(lambda ip: print(f"Sensor deleted: {ip}"))
    
    window.show()
    sys.exit(app.exec_())
