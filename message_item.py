from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QDoubleSpinBox, QFrame, QListWidgetItem
)
from PyQt5.QtCore import QTimer

class MessageItem:
    def __init__(self, message: str, name: str, send_callback, mode: str, format_func):
        self.raw_bytes = message.encode('utf-8', errors='replace')
        self.name = name
        self.label = QLabel()
        self.send_button = QPushButton("Send")
        self.send_button.setFixedWidth(60)
        self.schedule_checkbox = QCheckBox("Auto-send")
        self.interval_selector = QDoubleSpinBox()
        self.interval_selector.setSuffix(" s")
        self.interval_selector.setRange(0.1, 60.0)
        self.interval_selector.setValue(1.0)
        self.timer = QTimer()

        self.send_callback = send_callback

        self.send_button.clicked.connect(lambda: self.send())
        self.timer.timeout.connect(lambda: self.send())
        self.schedule_checkbox.toggled.connect(
            lambda checked: self.toggle_timer(checked)
        )

        self.update_label(mode, format_func)

        self.widget = QWidget()
        layout = QVBoxLayout()

        label_layout = QHBoxLayout()
        label_layout.addWidget(self.label)
        label_layout.addWidget(self.send_button)

        config_layout = QHBoxLayout()
        config_layout.addWidget(self.schedule_checkbox)
        config_layout.addWidget(QLabel("Interval:"))
        config_layout.addWidget(self.interval_selector)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)

        layout.addLayout(label_layout)
        layout.addLayout(config_layout)
        layout.addWidget(separator)
        layout.setContentsMargins(0, 0, 0, 0)

        self.widget.setLayout(layout)

        self.list_item = QListWidgetItem()
        self.list_item.setSizeHint(self.widget.sizeHint())

    def send(self):
        self.send_callback(self.raw_bytes, direction='sent')

    def toggle_timer(self, enabled):
        if enabled:
            self.timer.start(self.interval_selector.value() * 1000)
        else:
            self.timer.stop()

    def update_label(self, mode, format_func):
        formatted = format_func(self.raw_bytes, mode)
        self.label.setText(f"{self.name + ':' if self.name else ':'}{formatted}")

    def get_widget(self):
        return self.widget

    def get_list_item(self):
        return self.list_item

    def get_timer(self):
        return self.timer

    def get_raw_bytes(self):
        return self.raw_bytes
