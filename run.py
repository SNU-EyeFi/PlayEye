import cv2
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from gaze_tracking import GazeTracking
from util import EyeGuide
from util import Switch
from util import VerticalWindow, HorizontalWindow
from util import Touch
from util import LED
from audio import SimplePlay

from picamera2 import Picamera2
from libcamera import controls

class Runner():
    def __init__(self, window_type, verbose):

        # Initialize
        self.gaze = GazeTracking()
        self.touch = Touch()
        self.guide = EyeGuide() 
        self.switch = Switch()
        self.led = LED()

        self.verbose = verbose
        self.pastWrong = 5
        self.pastTarget = 5
        self.max_patience = 2

        # Initialize GUI
        self.app = QApplication([])
        if window_type == "vertical" :	
            self.window = VerticalWindow()	
        else: #if window_type == "horizontal" 
            self.window = HorizontalWindow(verbose)	

        self.window.show()

    def init_picam(self):
        picam2 = Picamera2()
        config = picam2.create_video_configuration( main = {"size": (480, 360), "format": "RGB888"})
        picam2.configure(config)
        picam2.start()
        picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
        return picam2

    def get_gaze_crop(self, left, right):
        if left is not None and right is not None:
            left_x, left_y = left
            right_x, right_y = right
            crop_center_x = int(0.5 * (left_x + right_x))
            crop_center_y = int(0.5 * (left_y + right_y))
            crop_height = 50  
            fixed_crop_width = 300 

            crop_left = max(0, crop_center_x - (fixed_crop_width // 2))
            crop_right = crop_left + fixed_crop_width

            crop_top = crop_center_y - (crop_height // 2)
            crop_bottom = crop_center_y + (crop_height // 2)
            cropped_frame_rgb = rgb_frame_raw[crop_top:crop_bottom, crop_left:crop_right]

            return cropped_frame_rgb
        else return None
        

    def run(self):
        
        self.guide.setMode("Round") 
        method = "Gaze"
        mode = self.guide.getMode()
        target = self.guide.getTarget()
        priorM = ("Off", "Off")
        priorTarget = 0
        idx = 0
        patience = 0
        play_instance = SimplePlay()

        picam2 = self.init_picam()

        while True:

            # Capture frame-by-frame
            frame_raw = picam2.capture_array("main")
            frame_raw = cv2.flip(frame_raw, 0)
            rgb_frame_raw = cv2.cvtColor(frame_raw, cv2.COLOR_BGR2RGB)
            if (priorM[0] != "Off"):
                self.window.set_image(rgb_frame_raw)

            # Listen for keyboard input
            if( self.window.key_set):
                key = self.window.key_recent
                self.window.key_set = False
            else:
                key = None

            # Press Esc to exit
            if key == Qt.Key_Escape:
                break

            # Get mode using rotary switch through GPIO
            method, mode = self.switch.getMode() 

            # For unstable switch
            if (None, None) == (method, mode):
                method = priorM[0]
                mode = priorM[1]

            # Change mode
            if (priorM != (method, mode)): 
                self.guide.setMode(mode)
                if( method != "Off"):
                    if priorM[0] == "Off": # if mode is changed from Off to On
                        play_instance.modeSelect()
                    self.led.showMode(mode)
                    target = self.guide.getTarget()
                    priorTarget =  0
                    idx = 0
                if mode == "Eight":
                    play_instance.eightMode()
                elif mode =="Round":
                    play_instance.roundMode()
                elif mode == "Shift":
                    play_instance.shiftMode()
                elif mode == "Random":
                    play_instance.touchMode()
                elif mode == "Off":
                    play_instance.quitMode()
                    self.led.light_all_off()
            priorM = (method, mode)
            
            # Emulate gaze success for debugging
            if key == Qt.Key_P:
                play_instance.targetSuccess()
                idx +=1
                patience = 0

            # Output LED and audio for successful round of mode
            if idx == len(target):
                play_instance.stageSuccess()
                for i in range (3):
                    self.led.light_all_white()
                    time.sleep(0.3)
                    self.led.light_all_off()
                    time.sleep(0.3)
                idx = 0
                
            # Show target for UI and LED
            if( method != "Off"):
                self.window.showTarget(target[idx])
            if( method != "Off" and priorTarget != target[idx]):
                self.led.light_all_off()
                self.led.light_on(target[idx])
                priorTarget = target[idx]
        
            # Evaluate gaze mode
            if (method == "Gaze"): 
                try:
                    self.gaze.refresh(frame_raw)
                except cv2.error as e:
                    pass
        
                frame = self.gaze.annotated_frame()
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.window.set_image(rgb_frame)
                block = self.gaze.is_where()   
                
                # Show gaze crop on UI
                left = self.gaze.pupil_left_coords()
                right = self.gaze.pupil_right_coords()
                cropped_frame_rgb = self.get_gaze_crop(left, right)
                if cropped_frame_rgb is not None:
                    self.window.set_crop(cropped_frame_rgb)

                if(target[idx] == block):
                    patience +=1
                    if(patience == self.max_patience): 
                        patience = 0
                        idx += 1
                        play_instance.targetSuccess()
                else:
                    patience = 0 
                    
                # Show gaze info on UI
                self.window.showGaze(self.gaze, block)
                
                # Show loading bar on UI
                self.window.showLoading(patience, self.max_patience)

            elif method == "Touch": 
                block = self.touch.is_where(self.window.key_recent)
                if(target[idx] == block): 
                    play_instance.animalSound(block)
                    self.led.showTouch(block)
                    target = self.guide.getTarget()
                    self.pastTarget = block
                
                elif block in [1, 2, 3, 4, 6, 7, 8, 9]:
                    if self.pastWrong != block and self.pastTarget != block :
                        self.led.showWrongTouch(block)
                        play_instance.targetWrong()
                        self.pastWrong = block      
                self.window.showTouch(block)
            
            self.window.showMode(method, mode)
            self.app.processEvents()


        
        


