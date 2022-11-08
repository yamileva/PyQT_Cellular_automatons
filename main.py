from PyQt5.QtWidgets import QApplication
import sys
from modules.MainWindow import MainWindow


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    MainWindow().show()
    sys.exit(app.exec_())
