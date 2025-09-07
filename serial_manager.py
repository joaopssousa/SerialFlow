import serial
import threading
import time

class SerialManager:
    def __init__(self):
        self.serial_port = None
        self._stop_event = threading.Event()
        self.read_thread = None
        self.receive_callback = None  # função definida pela interface para receber dados

    def connect(self, port, baudrate):
        self.serial_port = serial.Serial(port, baudrate, timeout=0.1)
        self._stop_event.clear()
        self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self.read_thread.start()

    def disconnect(self):
        self._stop_event.set()
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.serial_port = None

    def send(self, data: bytes):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.write(data)

    def is_connected(self):
        return self.serial_port and self.serial_port.is_open

    def _read_loop(self):
        while not self._stop_event.is_set():
            if self.serial_port and self.serial_port.in_waiting:
                try:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    print(f"[RECEBIDO RAW]: {data}")  # debug
                    if self.receive_callback:
                        self.receive_callback(data)
                except Exception as e:
                    print(f"Erro leitura: {e}")
            time.sleep(0.05)  # Evita CPU 100%
