import cv2
from PyQt5.QtCore import Qt

class Touch():
    def __init__(self):
        pass

    def is_where(self, key):
        if key == Qt.Key_1:
            return 1
        elif key == Qt.Key_2:
            return 2
        elif key == Qt.Key_3:
            return 3
        elif key == Qt.Key_4:
            return 4
        elif key == Qt.Key_5:
            return 5
        elif key == Qt.Key_6:
            return 6
        elif key == Qt.Key_7:
            return 7
        elif key == Qt.Key_8:
            return 8
        elif key == Qt.Key_9:
            return 9