"""Backend serial simples e funcional"""
import serial
import serial.tools.list_ports
from PySide6.QtCore import QObject, Signal, QThread
import time


class SerialReader(QObject):
    """Worker que lê dados em thread separada"""
    data_received = Signal(bytes)
    
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = True
    
    def run(self):
        while self.running and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    if data:
                        self.data_received.emit(data)
                time.sleep(0.01)  # 10ms poll
            except:
                break
    
    def stop(self):
        self.running = False


class SerialBackend(QObject):
    """Backend serial completo"""
    data_received = Signal(bytes)
    connected = Signal(str)  # port name
    disconnected = Signal()
    error = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.reader = None
        self.thread = None
    
    def connect(self, port, baudrate, bytesize=8, parity='N', stopbits=1):
        """Conecta à porta serial"""
        try:
            if(port == "loop://"):
                self.serial_port = serial.serial_for_url(port)
            else:
                self.serial_port = serial.Serial(
                    port=port,
                    baudrate=baudrate,
                    bytesize=bytesize,
                    parity=parity,
                    stopbits=stopbits,
                    timeout=0.1
                )
            
            # Inicia thread de leitura
            self.reader = SerialReader(self.serial_port)
            self.thread = QThread()
            self.reader.moveToThread(self.thread)
            
            self.reader.data_received.connect(self.data_received)
            self.thread.started.connect(self.reader.run)
            
            self.thread.start()
            self.connected.emit(port)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def disconnect(self):
        """Desconecta"""
        if self.reader:
            self.reader.stop()
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        
        self.serial_port = None
        self.reader = None
        self.thread = None
        self.disconnected.emit()
    
    def write(self, data):
        """Envia dados"""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.write(data)
            except Exception as e:
                self.error.emit(str(e))
    
    @staticmethod
    def list_ports():
        """Lista portas disponíveis"""
        return [p.device for p in serial.tools.list_ports.comports()]
