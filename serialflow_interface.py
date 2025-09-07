from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QLabel, QComboBox, QWidget, QListWidget, QInputDialog
)
from PyQt5.QtCore import QMetaObject, Qt, Q_ARG, QTimer
from serial_manager import SerialManager
from message_item import MessageItem
from utils import format_bytes
import serial.tools.list_ports

class SerialFlowInterface(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SerialFlow")
        self.setGeometry(100, 100, 800, 600)

        self.timers = []
        self.display_mode = 'ASCII'
        self.sent_messages = []
        self.received_messages = []
        self.saved_message_data = []
        self.serial = SerialManager()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        display_mode_layout = QHBoxLayout()
        self.ascii_button = QPushButton("ASCII")
        self.hex_button = QPushButton("Hex")
        self.ascii_button.setCheckable(True)
        self.hex_button.setCheckable(True)
        self.ascii_button.setChecked(True)
        self.ascii_button.clicked.connect(self.set_ascii_mode)
        self.hex_button.clicked.connect(self.set_hex_mode)
        display_mode_layout.addWidget(QLabel("Display as:"))
        display_mode_layout.addWidget(self.ascii_button)
        display_mode_layout.addWidget(self.hex_button)
        main_layout.addLayout(display_mode_layout)

        self.message_log = QTextEdit()
        self.message_log.setReadOnly(True)
        main_layout.addWidget(self.message_log)

        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.send_button = QPushButton("Send")
        self.save_button = QPushButton("Save Message")
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.save_button)
        main_layout.addLayout(input_layout)

        self.saved_messages_list = QListWidget()
        main_layout.addWidget(self.saved_messages_list)

        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Port:"))
        self.port_selector = QComboBox()
        self.refresh_ports()
        control_layout.addWidget(self.port_selector)
        control_layout.addWidget(QLabel("Baud Rate:"))
        self.baud_rate_selector = QComboBox()
        self.baud_rate_selector.addItems(["9600", "19200", "38400", "57600", "115200"])
        control_layout.addWidget(self.baud_rate_selector)
        self.connect_button = QPushButton("Connect")
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setEnabled(False)
        control_layout.addWidget(self.connect_button)
        control_layout.addWidget(self.disconnect_button)
        main_layout.addLayout(control_layout)

        self.send_button.clicked.connect(self.send_message)
        self.save_button.clicked.connect(self.save_message)
        self.connect_button.clicked.connect(self.connect_serial)
        self.disconnect_button.clicked.connect(self.disconnect_serial)
        self.serial.receive_callback = self.handle_received_data

    def refresh_ports(self):
        self.port_selector.clear()
        ports = [str(port.device) for port in serial.tools.list_ports.comports()]
        ports += ["/tmp/ttyV0", "/tmp/ttyV1"]
        self.port_selector.addItems(ports)

    def send_message(self):
        message = self.message_input.text()
        if message:
            raw = message.encode('utf-8', errors='replace')
            if self.serial.is_connected():
                self.serial.send(raw)
            self.sent_messages.append(raw)
            self.update_message_log()
            self.message_input.clear()

    def save_message(self):
        message = self.message_input.text()
        if message:
            name, ok = QInputDialog.getText(self, "Save Message", "Enter a name for the message:")
            if ok:
                item = MessageItem(message, name, self.send_saved_message, self.display_mode, format_bytes)
                list_item = item.get_list_item()
                self.saved_messages_list.addItem(list_item)
                self.saved_messages_list.setItemWidget(list_item, item.get_widget())
                self.timers.append(item.get_timer())
                self.saved_message_data.append(item)
                self.message_input.clear()

    def toggle_message_timer(self, enabled, timer, interval_selector):
        if enabled:
            interval = interval_selector.value() * 1000
            timer.start(interval)
        else:
            timer.stop()

    def send_saved_message(self, raw_bytes, direction='sent'):
        if self.serial.is_connected():
            self.serial.send(raw_bytes)
        self.sent_messages.append(raw_bytes)
        self.update_message_log()

    def connect_serial(self):
        port = self.port_selector.currentText()
        baud_rate = int(self.baud_rate_selector.currentText())
        try:
            self.serial.connect(port, baud_rate)
            self.message_log.append(f"Connected to {port} at {baud_rate} baud.")
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
        except Exception as e:
            self.message_log.append(f"Connection failed: {e}")

    def disconnect_serial(self):
        self.serial.disconnect()
        self.message_log.append("Disconnected.")
        self.connect_button.setEnabled(True)
        self.disconnect_button.setEnabled(False)

    def set_ascii_mode(self):
        self.display_mode = 'ASCII'
        self.ascii_button.setChecked(True)
        self.hex_button.setChecked(False)
        self.update_message_log()
        self.update_saved_messages_labels()

    def set_hex_mode(self):
        self.display_mode = 'HEX'
        self.hex_button.setChecked(True)
        self.ascii_button.setChecked(False)
        self.update_message_log()
        self.update_saved_messages_labels()

    def update_message_log(self):
        self.message_log.clear()
        for raw in self.sent_messages:
            formatted = format_bytes(raw, self.display_mode)
            self.message_log.append(f"Sent: {formatted}")
        for raw in self.received_messages:
            formatted = format_bytes(raw, self.display_mode)
            self.message_log.append(f"Received: {formatted}")

    def update_saved_messages_labels(self):
        for item in self.saved_message_data:
            item.update_label(self.display_mode, format_bytes)

    def handle_received_data(self, data):
        print("[RECEBIDO RAW]:", data)
        self.received_messages.append(data)
        QTimer.singleShot(0, self.update_message_log)
