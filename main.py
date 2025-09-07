import sys
from PyQt5.QtWidgets import QApplication
from serialflow_interface import SerialFlowInterface

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialFlowInterface()
    window.show()
    sys.exit(app.exec_())