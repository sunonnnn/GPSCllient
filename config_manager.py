import sys
import yaml
import os
from PyQt5.QtWidgets import (
    QApplication, QDialog,
    QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt
from delete_list_widget import DeleteListWidget


class ConfigManager(QDialog):
    def __init__(self, config_path="./config/config.yaml", parent=None):
        super().__init__(parent)
        self.config_path = config_path
        self.config_data = None
        self.result_data = None
        
        self.load_config()
        self.setup_ui()
        self.populate_fields()
        self.connect_signals()

    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config_data = yaml.safe_load(f)
            else:
                self.config_data = {}
        except Exception as e:
            print(f"Config load error: {e}")
            self.config_data = {}

    def setup_ui(self):
        self.setWindowTitle("Configuration")
        self.setFixedSize(440, 320)

        # ================== LEFT ==================
        group_settings = QGroupBox("Settings")
        settings_layout = QVBoxLayout(group_settings)

        # ---- Naver ----
        group_naver = QGroupBox("Naver Client")
        naver_layout = QGridLayout(group_naver)

        self.naver_id = QLineEdit()
        self.naver_pw = QLineEdit()

        naver_layout.addWidget(QLabel("Client ID"), 0, 0)
        naver_layout.addWidget(self.naver_id, 0, 1)
        naver_layout.addWidget(QLabel("Client PW"), 1, 0)
        naver_layout.addWidget(self.naver_pw, 1, 1)

        # ---- NTRIP ----
        group_ntrip = QGroupBox("NTRIP")
        ntrip_layout = QGridLayout(group_ntrip)

        self.ntrip_addr = QLineEdit()
        self.ntrip_port = QLineEdit()
        self.ntrip_id = QLineEdit()
        self.ntrip_pw = QLineEdit()
        self.ntrip_mount = QLineEdit()

        ntrip_layout.addWidget(QLabel("Address"), 0, 0)
        ntrip_layout.addWidget(self.ntrip_addr, 0, 1)
        ntrip_layout.addWidget(QLabel("Port"), 1, 0)
        ntrip_layout.addWidget(self.ntrip_port, 1, 1)
        ntrip_layout.addWidget(QLabel("ID"), 2, 0)
        ntrip_layout.addWidget(self.ntrip_id, 2, 1)
        ntrip_layout.addWidget(QLabel("Password"), 3, 0)
        ntrip_layout.addWidget(self.ntrip_pw, 3, 1)
        ntrip_layout.addWidget(QLabel("Mount"), 4, 0)
        ntrip_layout.addWidget(self.ntrip_mount, 4, 1)

        settings_layout.addWidget(group_naver)
        settings_layout.addSpacing(8)
        settings_layout.addWidget(group_ntrip)
        settings_layout.addSpacing(8)
        settings_layout.addStretch()

        # ================== RIGHT ==================
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Sensors"))

        self.list_widget = DeleteListWidget("./icons/minus_circle_red.svg")
        self.list_widget.setFixedWidth(190)
        right_layout.addWidget(self.list_widget)

        input_layout = QHBoxLayout()
        self.list_ip = QLineEdit()
        self.list_ip.setPlaceholderText("Enter IP address")
        self.btn_add = QPushButton("+")
        self.btn_add.setFixedWidth(32)

        input_layout.addWidget(self.list_ip)
        input_layout.addWidget(self.btn_add)

        right_layout.addLayout(input_layout)

        # ================== BOTTOM ==================
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.btn_save = QPushButton("Save")
        self.btn_ok = QPushButton("OK")
        self.btn_save.setFixedWidth(90)
        self.btn_ok.setFixedWidth(90)

        bottom_layout.addWidget(self.btn_save)
        bottom_layout.addSpacing(15)
        bottom_layout.addWidget(self.btn_ok)
        bottom_layout.addStretch()

        # ================== MAIN ==================
        main_layout = QHBoxLayout()
        main_layout.addWidget(group_settings)
        main_layout.addLayout(right_layout)

        outer_layout = QVBoxLayout(self)
        outer_layout.addLayout(main_layout)
        outer_layout.addLayout(bottom_layout)

    def populate_fields(self):
        if not self.config_data:
            return

        # Naver Client
        if 'naver_client' in self.config_data:
            naver = self.config_data['naver_client']
            self.naver_id.setText(naver.get('id', ''))
            self.naver_pw.setText(naver.get('key', ''))

        # NTRIP Settings
        if 'ntrip_settings' in self.config_data:
            ntrip = self.config_data['ntrip_settings']
            self.ntrip_addr.setText(ntrip.get('host_address', ''))
            self.ntrip_port.setText(str(ntrip.get('host_port', '')))
            self.ntrip_id.setText(ntrip.get('user_id', ''))
            self.ntrip_pw.setText(ntrip.get('user_pw', ''))
            self.ntrip_mount.setText(ntrip.get('mount_point', ''))

        # Sensors IP
        if 'sensors_ip' in self.config_data:
            for ip in self.config_data['sensors_ip'].keys():
                self.list_widget.add_item(ip)

    def connect_signals(self):
        """버튼 시그널 연결"""
        self.btn_add.clicked.connect(self.add_sensor)
        self.btn_save.clicked.connect(self.save_config)
        self.btn_ok.clicked.connect(self.ok_clicked)
        self.list_ip.returnPressed.connect(self.add_sensor)

    def add_sensor(self):
        """센서 IP를 리스트에 추가"""
        ip = self.list_ip.text().strip()
        if not ip:
            return

        self.list_widget.add_item(ip)
        self.list_ip.clear()

    def get_current_data(self):
        sensors = {}
        for i in range(self.list_widget.count()):
            item = self.list_widget.listWidget.item(i)
            widget = self.list_widget.listWidget.itemWidget(item)
            label = widget.findChild(QLabel)
            if label:
                ip = label.text().strip()
                ch = f"ch{i+1}"
                sensors[ip] = ch

        data = {
            'naver_client': {
                'id': self.naver_id.text(),
                'key': self.naver_pw.text()
            },
            'ntrip_settings': {
                'host_address': self.ntrip_addr.text(),
                'host_port': int(self.ntrip_port.text()) if self.ntrip_port.text() else 0,
                'user_id': self.ntrip_id.text(),
                'user_pw': self.ntrip_pw.text(),
                'mount_point': self.ntrip_mount.text()
            },
            'sensors_ip': sensors
        }
        
        return data

    def save_config(self):
        try:
            if self.config_data is None:
                self.config_data = {}
            
            current_data = self.get_current_data()
            
            self.config_data['naver_client'] = current_data['naver_client']
            self.config_data['ntrip_settings'] = current_data['ntrip_settings']
            self.config_data['sensors_ip'] = current_data['sensors_ip']

            config_dir = os.path.dirname(self.config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config_data, f, default_flow_style=False, allow_unicode=True)

            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration:\n{e}")

    def ok_clicked(self):
        self.result_data = self.get_current_data()
        self.accept()

    def get_result(self):
        return self.result_data


def main():
    app = QApplication(sys.argv)
    
    config_manager = ConfigManager()
    config_manager.show()
    
    app.exec_()
    
    result = config_manager.get_result()
    if result:
        print("\n=== Returned Data ===")
        print(yaml.dump(result, default_flow_style=False, allow_unicode=True))


if __name__ == "__main__":
    main()
