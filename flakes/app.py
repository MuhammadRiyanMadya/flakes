####### Creating Simplest Window
##from PyQt6.QtCore import QSize, Qt
##from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
##import sys
##
##class MainWindow(QMainWindow):
##    def __init__(self):
##        super().__init__()
##        self.setWindowTitle("My App")
##        self.setMinimumSize(1200,1200)
##        button = QPushButton("Press Me!")
##        button.setCheckable(True)
##        button.clicked.connect(self.the_button_was_clicked)
##        self.setCentralWidget(button)
##        
##    def the_button_was_clicked(self, checked):
##        print("Clicked!", checked)
##
##    
##app = QApplication([])
##window = MainWindow()
##window.show()
##
##app.exec()

####### Signals and slots

from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
import sys
from random import choice

window_titles = [
    'My App',
    'My App',
    'Still My App',
    'Still My App',
    'What on earth',
    'What on earth',
    'This is surprising',
    'This is surprising',
    'Something when wrong'
    ]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.n_times_clicked = 0

        self.setWindowTitle("My App")

        self.button = QPushButton("Press Me!")
        self.button.clicked.connect(self.the_button_was_clicked)

        self.windowTitleChanged.connect(self.the_window_title_changed)

        self.setCentralWidget(self.button)

    def the_button_was_clicked(self):
        print("Clicked.")
        new_window_title = choice(window_titles)
        print(Setting title


