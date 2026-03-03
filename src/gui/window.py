import threading
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QToolBar

class GUI(QMainWindow):
    def __init__(self, version):
        super().__init__()
        # Main window
        self.resize(400, 300)
        self.setWindowTitle(f'FlightGear BlueSky plugin v{version}')

        # Toolbar
        self.toolbar = QToolBar("toolbar")
        self.addToolBar(self.toolbar)
        
        # Toolbar items
        settings_button = QAction("Settings", self)
        settings_button.setStatusTip("Settings button")
        self.toolbar.addAction(settings_button)

        # Show GUI
        self.show()