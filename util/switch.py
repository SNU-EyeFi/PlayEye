import cv2
from util import EyeGuide
from PyQt5.QtCore import Qt
import RPi.GPIO as GPIO

pos_list = [23, 24, 25, 17]
GPIO.setmode(GPIO.BCM)

class Switch():    
    def __init__(self):
        for i in pos_list:
            GPIO.setup(i, GPIO.IN)
            
    def getMode(self):
        mode = None
        method = None

        if GPIO.input(23) == 1:
            mode = "Round"
            method = "Gaze"
        
        elif GPIO.input(24) == 1:
            mode = "Eight"
            method = "Gaze"
        
        elif GPIO.input(25) == 1:
            mode = "Shift"
            method = "Gaze"

        elif GPIO.input(17) == 1:
            mode = "Random"
            method = "Touch"
            
        else:
            mode = "Off"
            method = "Off"
            
        return method, mode
            
        