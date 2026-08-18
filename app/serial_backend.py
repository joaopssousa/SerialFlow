"""Backend serial simples e funcional"""
import serial
import serial.tools.list_ports
from PySide6.QtCore import QObject, Signal, QThread
import time


def read_control_lines(serial_port):
    """Lê o estado das linhas de controle (entradas e saídas) da porta"""
    lines = {}
    for name in ("cts", "dsr", "ri", "cd", "rts", "dtr"):
        try:
            lines[name] = bool(getattr(serial_port, name))
        except Exception:
            lines[name] = False
    return lines


class SerialReader(QObject):
    """Worker que lê dados em thread separada"""
    data_received = Signal(bytes)
    lines_changed = Signal(dict)

    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = True
        self._last_lines = None

    def run(self):
        poll_count = 0
        while self.running and self.serial_port.is_open:
            try:
                if self.serial_port.in_waiting:
                    data = self.serial_port.read(self.serial_port.in_waiting)
                    if data:
                        self.data_received.emit(data)
                poll_count += 1
                if poll_count >= 10:  # linhas de controle a cada ~100ms
                    poll_count = 0
                    lines = read_control_lines(self.serial_port)
                    if lines != self._last_lines:
                        self._last_lines = lines
                        self.lines_changed.emit(lines)
                time.sleep(0.01)  # 10ms poll
            except:
                break

    def stop(self):
        self.running = False


class SerialBackend(QObject):
    """Backend serial completo"""
    data_received = Signal(bytes)
    lines_changed = Signal(dict)
    connected = Signal(str)  # port name
    disconnected = Signal()
    error = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.reader = None
        self.thread = None
    
    def connect(self, port, baudrate, bytesize=8, parity='N', stopbits=1, rtscts=False):
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
                    timeout=0.1,
                    rtscts=rtscts
                )
                self._disable_hupcl()

            # Inicia thread de leitura
            self.reader = SerialReader(self.serial_port)
            self.thread = QThread()
            self.reader.moveToThread(self.thread)

            self.reader.data_received.connect(self.data_received)
            self.reader.lines_changed.connect(self.lines_changed)
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
    
    def _disable_hupcl(self):
        """Mantém DTR/RTS estáveis entre conexões (sem HUPCL).

        O kernel Linux sempre assenta o DTR no open(); se a linha já estava
        alta da conexão anterior não há borda — e sem borda o dispositivo
        (ex: Arduino) não reseta. Só a primeira conexão após plugar o cabo
        ainda gera o pulso, o que é inevitável no Linux.
        """
        try:
            import termios
            fd = self.serial_port.fileno()
            attrs = termios.tcgetattr(fd)
            attrs[2] &= ~termios.HUPCL
            termios.tcsetattr(fd, termios.TCSANOW, attrs)
        except Exception:
            pass  # Windows ou porta virtual: flag não existe/não se aplica

    def set_rts(self, state):
        """Altera a linha RTS com a porta aberta (flow control manual)"""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.rts = state
            except Exception as e:
                self.error.emit(str(e))

    def set_dtr(self, state):
        """Altera a linha DTR com a porta aberta"""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.dtr = state
            except Exception as e:
                self.error.emit(str(e))

    def set_flow_control(self, rtscts):
        """Liga/desliga o hardware flow control com a porta aberta"""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.rtscts = rtscts
            except Exception as e:
                self.error.emit(str(e))

    def get_lines(self):
        """Estado atual das linhas de controle, ou None se desconectado"""
        if self.serial_port and self.serial_port.is_open:
            return read_control_lines(self.serial_port)
        return None

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
