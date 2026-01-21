from PyQt5.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, pyqtSignal


class DeleteListWidget(QWidget):

    itemDeleted = pyqtSignal(str)

    def __init__(self, icon_path: str, parent=None):
        super().__init__(parent)

        self.icon_path = icon_path

        self.listWidget = QListWidget()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.listWidget)

    def add_item(self, text: str):
        item = QListWidgetItem(self.listWidget)

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 4, 10, 4)

        label = QLabel(text)

        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(self.icon_path))
        delete_btn.setIconSize(QSize(14, 14))
        delete_btn.setFixedSize(22, 22)

        delete_btn.setStyleSheet("""
        QPushButton {
            border: none;
            background: transparent;
        }
        QPushButton:hover {
            background-color: rgba(0, 0, 0, 0.08);
            border-radius: 4px;
        }
        """)

        row_widget.setStyleSheet("""
        QPushButton {
            opacity: 0;
        }
        QWidget:hover QPushButton {
            opacity: 1;
        }
        """)

        row_layout.addWidget(label)
        row_layout.addStretch()
        row_layout.addWidget(delete_btn)

        item.setSizeHint(row_widget.sizeHint())
        self.listWidget.setItemWidget(item, row_widget)

        delete_btn.clicked.connect(
            lambda: self._on_delete_clicked(item, text)
        )

    def _on_delete_clicked(self, item, text):
        row = self.listWidget.row(item)
        self.listWidget.takeItem(row)
        self.itemDeleted.emit(text)

    def clear(self):
        self.listWidget.clear()

    def count(self) -> int:
        return self.listWidget.count()
