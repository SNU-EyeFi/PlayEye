from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QWidget, QStackedLayout, QGridLayout, QProgressBar, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer
import cv2
from PIL import Image
import numpy as np
from PIL import Image
import numpy as np

class VerticalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.key_set = False
        self.key_recent = 1
        self.loading_patience = 0
        self.max_loading_patience = 5

        self.color_list = [
            (255, 53, 0),        
            (64, 16, 204),      
            (186, 204, 0),     
            (5, 204, 16),        
            (255, 255, 255),    
            (0, 81, 12),        
            (204, 16, 56),     
            (25, 160, 204),   
            (204, 9, 10)         
        ]
        self.formerBlock = None

        # Set window title
        self.setWindowTitle("PlayEye")

        # Create a main widget to hold other widgets
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        self.main_widget.setStyleSheet("background-color: white;")

        # Create a vertical layout for the main widget
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Create a label for the brand logo at the top
        self.logo_label = QLabel(self)
        self.logo_pixmap = QPixmap("./images/logo.png")  
        w = int(self.main_widget.width()/3)
        h = int(self.logo_pixmap.height()/2)
        self.logo_label.setPixmap(self.logo_pixmap.scaled(w, h, aspectRatioMode=Qt.KeepAspectRatio))
        self.main_layout.addWidget(self.logo_label, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # Show mode selection
        self.mode_label = QLabel("Mode: ", self)
        self.mode_label.setStyleSheet("font-size: 40px; font-weight: bold;")
        self.mode_label.setAlignment(Qt.AlignLeft)
        self.main_layout.addWidget(self.mode_label, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # Create a widget for the frame and semi-transparent boxes
        self.frame_widget = QWidget(self)
        self.frame_layout = QHBoxLayout(self.frame_widget)
        self.frame_widget.setStyleSheet("border: 2px solid #888888; border-radius: 5px;")
        self.frame_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.frame_widget, alignment=Qt.AlignTop | Qt.AlignHCenter)

        # Create a label for the frame in the center
        self.frame_label = QLabel(self)
        self.box_layout = QHBoxLayout(self.frame_label)
        self.box_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_layout.addWidget(self.frame_label) 

        # Create a grid layout for the widget
        self.box_widget = QWidget(self)
        self.grid_layout = QGridLayout(self.box_widget)
        self.box_widget.setStyleSheet("background-color: transparent; border: none;")
        self.box_layout.addWidget(self.box_widget)

        self.boxes = []
        for row in range(3):
            for column in range(3):
                box = QLabel(self)
                rgb = self.color_list[column+row*3]
                color = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0)"
                box.setStyleSheet(f"background-color: {color}; border: none;")
                self.boxes.append(box)
                self.grid_layout.addWidget(box, row, column)

        # Create widget for looking at, target
        self.look_widget = QWidget(self)
        self.look_layout = QHBoxLayout(self.look_widget)
        self.target = QLabel("Target: ", self.look_widget)
        self.target.setStyleSheet("font-size: 15px; font-weight: bold; border: none;")
        
        self.current = QLabel("Current: ", self.look_widget)
        self.current.setStyleSheet("font-size: 15px; font-weight: bold; border: none;")
        self.look_layout.addWidget(self.target, alignment=Qt.AlignCenter)
        self.look_layout.addWidget(self.current, alignment=Qt.AlignCenter)
        self.main_layout.addWidget(self.look_widget)


        # Add a border around the look_widget (self.look_widget)
        self.look_widget.setStyleSheet("border: 2px solid #888888; border-radius: 5px;")

                
        # Create horizontal widgets for the text explanations and eye crops
        self.hori_widget = QWidget(self)
        self.hori_layout = QHBoxLayout(self.hori_widget)
        self.hori_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.addWidget(self.hori_widget)


        # Add a border around the horizontal widget (self.hori_widget)
        self.hori_widget.setStyleSheet("border: 2px solid #888888; border-radius: 5px;")

        # Create a frame to hold the explanations widget and add a border
        self.explanations_frame = QFrame(self)
        self.explanations_frame.setFrameShape(QFrame.Box)
        self.explanations_frame.setLineWidth(1)  # Adjust the width of the border as needed
        self.explanations_frame.setStyleSheet("background-color: #f0f0f0; border: 2px solid #888888; border-radius: 5px;")

        # Create a layout for the explanations widget
        self.explanations_layout = QVBoxLayout(self.explanations_frame)
        self.explanations_layout.setContentsMargins(10, 10, 10, 10)

        # Add the explanations widget to the main layout (self.hori_layout)
        self.hori_layout.addWidget(self.explanations_frame)

        # Create text labels for the explanations
        self.explanation_labels = []
        explanations = ["Horizontal: ", "Vertical: ", "Blinking: "]
        for explanation in explanations:
            label = QLabel(explanation)
            self.explanation_labels.append(label)
            self.explanations_layout.addWidget(label, alignment=Qt.AlignLeft)
            # Remove borders from individual labels
            label.setStyleSheet("border: none;")
                      
        # create a widget for displaying eyes next to text explanations
        self.eyecrop_widget = QWidget(self)
        self.eyecrop_layout = QVBoxLayout(self.eyecrop_widget)
        self.hori_layout.addWidget(self.eyecrop_widget)
        self.eyecrop_widget.setStyleSheet("border: none;")
        
        # Add description for eye crop
        self.eyedesc_label = QLabel("Eye Crop", self)
        font = self.eyedesc_label.font()
        font.setPointSize(16)  
        font.setBold(True)
        self.eyedesc_label.setFont(font)
        self.eyecrop_layout.addWidget(self.eyedesc_label, alignment=Qt.AlignCenter)

        # Crop eye region
        self.eyecrop_label = QLabel(self)
        self.eyecrop_label.setFixedWidth(200)
        self.eyecrop_label.setFixedHeight(40)
        self.eyecrop_layout.addWidget(self.eyecrop_label, alignment=Qt.AlignHCenter) 
        
        # loading bar region
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        # Set the initial width of the progress bar (e.g., 300 pixels)
        self.progress_bar.setFixedWidth(200)
        # Remove the percentage text from the progress bar
        # Hide the percentage text
        self.progress_bar.setTextVisible(False)
        self.eyecrop_layout.addWidget(self.progress_bar, alignment=Qt.AlignHCenter) 


    def set_image(self, image):
        height, width, channel = image.shape
        bytes_per_line = channel * width
        w = int(self.main_widget.width()* 0.9)
        h = int(self.main_widget.height() * w / self.main_widget.width()* 0.9)
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)
        self.frame_label.setPixmap(q_pixmap.scaled(int(w), int(h), aspectRatioMode=Qt.KeepAspectRatio))

    def set_crop(self, image, bytes):
        height, width, channel = image.shape
        bytes_per_line = channel * width
        w = int(self.eyecrop_label.width() * 0.8)
        h = int(self.eyecrop_label.height() * 0.8)
        q_image = QImage(bytes, width, height, bytes_per_line, QImage.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)
        if not q_pixmap.isNull():
            self.eyecrop_label.setPixmap(q_pixmap.scaled(w, h, aspectRatioMode=Qt.KeepAspectRatio))

    def showGaze(self, gaze, block):
        hori = gaze.horizontal_ratio()
        verti = gaze.vertical_ratio()
        blink = -1
        if (gaze.pupils_located):
            blink = (gaze.eye_left.blinking+gaze.eye_right.blinking)/2
           
        if(hori != None):
            self.explanation_labels[0].setText("Horizontal: "+ str(round(hori,2)))
        if(verti != None):
            self.explanation_labels[1].setText("Vertical: "+ str(round(verti,2)))
        if(blink != None and blink != -1):
            blink = "O" if blink > 3.8 else "X"
            self.explanation_labels[2].setText("Blinking: " + blink)
        
        if block != 0:
            color = self.color_list[block-1] if block != 5 else (0, 0, 0)
            text = f"Looking at <span style='color: rgb{color};'>{block}</span>"
            self.current.setText(text)
    
    def showTouch(self, block):
        if block != None:
            self.formerBlock = block
            color = self.color_list[block-1] if block != 5 else (0, 0, 0)
            text = f"Touched <span style='color: rgb{color};'>{block}</span>"
            self.current.setText(text)
        else: #So that former choice is displayed
            block = self.formerBlock
        
    def showTarget(self, target):
        if target != None:
            self.turn_off_all_box()
            self.set_box_visibility(target-1, True)
            color = self.color_list[target-1]
            text = f"Target is <span style='color: rgb{color};'>{target}</span>"
            self.target.setText(text)


    def showSuccess(self):
        return

    def showLoading(self, patience, max_patience):
        progress = int(patience / max_patience * 100)
        self.progress_bar.setValue(progress)
    
    def showMode(self, method, mode):
        text = f"<span style='color: #FFC701;'>{mode} Mode </span> <span style = 'color: #808080; '> Selected with {method} </span>"s
        self.mode_label.setText(text)

    def set_box_visibility(self, index, visible):
        if 0 <= index < len(self.boxes):
            box = self.boxes[index]
            rgb = self.color_list[index]
            if visible:
                color = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 100)"
                box.setStyleSheet(f"background-color: {color};")
            else:
                color = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0)"
                box.setStyleSheet(f"background-color: {color};")

    def turn_off_all_box(self):
        for index in range(len(self.boxes)):
            self.set_box_visibility(index, False)

    def keyPressEvent(self, e):
        self.key_recent = e.key()
        self.key_set = True

class HorizontalWindow(QMainWindow):
    def __init__(self, verbose):
        super().__init__()
        self.key_set = False
        self.key_recent = 1
        self.loading_patience = 0
        self.max_loading_patience = 5
        self.verbose = verbose

        self.color_list = [
            (255, 53, 0),        
            (64, 16, 204),      
            (186, 204, 0),     
            (5, 204, 16),        
            (255, 255, 255),    
            (0, 81, 12),        
            (204, 16, 56),     
            (25, 160, 204),   
            (204, 9, 10)         
        ]
        self.formerBlock = None

        # Set window title
        self.setWindowTitle("EyeFI")
        self.resize(800, 600)	

        # Create a main widget to hold other widgets	
        self.base_widget = QWidget(self)	
        self.setCentralWidget(self.base_widget)	
        self.base_widget.setStyleSheet("background-color: white;")	
        # Create a vertical layout for the main widget	
        self.base_layout = QHBoxLayout(self.base_widget)	
        self.base_layout.setContentsMargins(20, 20, 20, 20)

        # Create a main widget to hold other widgets
        self.main_widget = QWidget(self)
        self.main_widget.setStyleSheet("background-color: white;")

        # Create a vertical layout for the main widget
        self.main_layout = QHBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)	
        self.base_layout.addWidget(self.main_widget)

        self.left_margin_widget = QWidget(self)
        self.left_margin_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)	
        self.left_margin_layout = QVBoxLayout(self.left_margin_widget)	
        self.main_layout.addWidget(self.left_margin_widget, alignment=Qt.AlignLeft)

        if self.verbose :	
            self.left_margin_width = self.main_widget.width() / 5	
        else:	
            self.left_margin_width = self.main_widget.width() / 4

        # Create a label for the brand logo at the top
        self.logo_label = QLabel(self)
        self.logo_pixmap = QPixmap("./images/logo.png") 
        w = int(self.left_margin_width)	
        h = int(self.logo_pixmap.height()/(self.logo_pixmap.width()) * self.left_margin_width)	
        self.logo_label.setPixmap(self.logo_pixmap.scaled(w, h, aspectRatioMode=Qt.KeepAspectRatio))
        self.left_margin_layout.addWidget(self.logo_label, alignment=Qt.AlignTop)

        # Show mode selection
        self.mode_label = QLabel("Mode: ", self)
        self.mode_label.setStyleSheet("font-size: 40px; font-weight: bold;")
        self.mode_label.setAlignment(Qt.AlignLeft)
        self.left_margin_layout.addWidget(self.mode_label, alignment=Qt.AlignTop)

        # Create a widget for the frame and semi-transparent boxes
        self.frame_widget = QWidget(self)
        self.frame_layout = QHBoxLayout(self.frame_widget)
        self.frame_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.frame_widget.setStyleSheet("border: 2px solid #888888; border-radius: 5px;")
        self.frame_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.frame_widget)

        # Create a label for the frame in the center
        self.frame_label = QLabel(self)
        self.box_layout = QHBoxLayout(self.frame_label)
        self.box_layout.setContentsMargins(0, 0, 0, 0)
        self.frame_layout.addWidget(self.frame_label)
        
        # Create a grid layout for the widget
        self.box_widget = QWidget(self)
        self.grid_layout = QGridLayout(self.box_widget)
        self.box_widget.setStyleSheet("background-color: transparent; border: none;")
        self.box_layout.addWidget(self.box_widget)

        self.boxes = []
        for row in range(3):
            for column in range(3):
                box = QLabel(self)
                rgb = self.color_list[column+row*3]
                color = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0)"
                box.setStyleSheet(f"background-color: {color}; border: none;")
                self.boxes.append(box)
                self.grid_layout.addWidget(box, row, column)


        # Create widget for looking at, target
        self.look_widget = QWidget(self)
        self.look_layout = QVBoxLayout(self.look_widget)
        self.target = QLabel("Target: ", self.look_widget)
        self.target.setStyleSheet("font-size: 30px; font-weight: bold; border: none;")
        
        self.current = QLabel("Current: ", self.look_widget)
        self.current.setStyleSheet("font-size: 30px; font-weight: bold; border: none;")
        self.look_layout.addWidget(self.target, alignment=Qt.AlignCenter)
        self.look_layout.addWidget(self.current, alignment=Qt.AlignCenter)
        self.left_margin_layout.addWidget(self.look_widget, alignment=Qt.AlignBottom)


        # Add a border around the look_widget (self.look_widget)
        self.look_widget.setStyleSheet("border: 2px solid #888888; border-radius: 5px;")

                
        # Create horizontal widgets for the text explanations and eye crops
        self.verti_widget = QWidget(self)
        self.verti_layout = QVBoxLayout(self.verti_widget)
        self.verti_layout.setContentsMargins(10, 10, 10, 10)
        self.left_margin_layout.addWidget(self.verti_widget, alignment=Qt.AlignBottom)


        # Add a border around the horizontal widget (self.hori_widget)
        self.verti_widget.setStyleSheet("border: 2px solid #888888; border-radius: 5px;")

        # Create a frame to hold the explanations widget and add a border
        self.explanations_frame = QFrame(self)
        self.explanations_frame.setFrameShape(QFrame.Box)
        self.explanations_frame.setLineWidth(1)  # Adjust the width of the border as needed
        self.explanations_frame.setStyleSheet("background-color: #f0f0f0; border: 2px solid #888888; border-radius: 5px;")

        # Create a layout for the explanations widget
        self.explanations_layout = QVBoxLayout(self.explanations_frame)
        self.explanations_layout.setContentsMargins(10, 10, 10, 10)

        # Add the explanations widget to the main layout (self.hori_layout)
        self.verti_layout.addWidget(self.explanations_frame)

        # Create text labels for the explanations
        self.explanation_labels = []
        explanations = ["Horizontal: ", "Vertical: ", "Blinking: "]
        for explanation in explanations:
            label = QLabel(explanation)
            self.explanation_labels.append(label)
            self.explanations_layout.addWidget(label, alignment=Qt.AlignLeft)
            # Remove borders from individual labels
            label.setStyleSheet("border: none; font-size: 20px")
                      
        # create a widget for displaying eyes next to text explanations
        self.eyecrop_widget = QWidget(self)
        self.eyecrop_layout = QVBoxLayout(self.eyecrop_widget)
        self.verti_layout.addWidget(self.eyecrop_widget, alignment=Qt.AlignCenter)
        self.eyecrop_widget.setStyleSheet("border: none;")
        
        # Add description for eye crop
        self.eyedesc_label = QLabel("Eye Crop", self)
        font = self.eyedesc_label.font()
        font.setPointSize(30)  # 원하는 크기로 조정
        font.setBold(True)
        self.eyedesc_label.setFont(font)
        self.eyecrop_layout.addWidget(self.eyedesc_label, alignment=Qt.AlignCenter)

        # Crop eye region
        self.eyecrop_label = QLabel(self)
        self.eyecrop_label.setFixedWidth(self.left_margin_width-40)
        self.eyecrop_label.setFixedHeight(40)
        self.eyecrop_layout.addWidget(self.eyecrop_label, alignment=Qt.AlignCenter)  
        
        # loading bar region
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        # Set the initial width of the progress bar (e.g., 300 pixels)
        self.progress_bar.setFixedWidth(self.left_margin_width-40)
        # Remove the percentage text from the progress bar
        # Hide the percentage text
        self.progress_bar.setTextVisible(False)
        self.eyecrop_layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        if self.verbose:
            self.right_margin_widget = QWidget(self)
            self.right_margin_layout = QVBoxLayout(self.right_margin_widget)
            
            self.right_margin_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            self.left_margin_width = self.main_widget.width() / 5
            self.left_margin_widget.setFixedWidth(self.left_margin_width)
            self.frame_widget.setFixedWidth(self.left_margin_width*2.7)
            self.right_margin_widget.setFixedWidth(self.left_margin_width)
            self.main_layout.addWidget(self.right_margin_widget, alignment=Qt.AlignLeft)
            
            # Create a layout for the explanations widget
            self.explanations_wrapper = QFrame(self)
            self.explanations_wrapper.setFrameShape(QFrame.Box)
            self.explanations_wrapper.setLineWidth(1)  # Adjust the width of the border as needed
            self.explanations_wrapper.setStyleSheet("background-color: #f0f0f0; border: 2px solid #888888; border-radius: 5px;")

            self.right_margin_layout.addWidget(self.explanations_wrapper)
            self.explanations_wrapper_layout = QHBoxLayout(self.explanations_wrapper)
            self.explanations_frame2_1 = QFrame(self)
            self.explanations_frame2_2 = QFrame(self)
            self.explanations_frame2_1.setStyleSheet("border: none;")
            self.explanations_frame2_2.setStyleSheet("border: none;")

            self.explanations_layout2_1 = QVBoxLayout(self.explanations_frame2_1)
            self.explanations_layout2_1.setContentsMargins(10, 10, 10, 10)

            self.explanations_layout2_2 = QVBoxLayout(self.explanations_frame2_2)
            self.explanations_layout2_2.setContentsMargins(10, 10, 10, 10)

            # Add the explanations widget to the main layout (self.verti_layout)
            self.explanations_wrapper_layout.addWidget(self.explanations_frame2_1, alignment=Qt.AlignTop)
            self.explanations_wrapper_layout.addWidget(self.explanations_frame2_2, alignment=Qt.AlignTop)

            # Create text labels for the explanations
            self.explanation_labels2_1 = []
            self.explanation_labels2_2 = []

            explanations2 = ["Left X: ", "Left Y: ", "Right X: ", "Right Y: ", "Left origin X: ", "Left origin Y: ", "Right origin X: ", "Right origin Y: ", "Left relative X: ", "Left relative Y: ", "Right relative X: ", "Right relative Y: ", "Left center X: ", "Left center Y: ", "Right center X: ", "Right center Y: "]
            for explanation in explanations2:
                label_1 = QLabel(explanation)
                label_2 = QLabel(explanation)

                self.explanation_labels2_1.append(label_1)
                self.explanations_layout2_1.addWidget(label_1, alignment=Qt.AlignTop|Qt.AlignLeft)
                self.explanation_labels2_2.append(label_2)
                self.explanations_layout2_2.addWidget(label_2, alignment=Qt.AlignTop|Qt.AlignRight)
                # Remove borders from individual labels
                label_1.setStyleSheet("border: none; font-size: 23px")
                label_2.setStyleSheet("border: none; font-size: 23px")

        else:
            self.left_margin_width = self.main_widget.width() / 4
            self.left_margin_widget.setFixedWidth(self.left_margin_width)
            self.frame_widget.setFixedWidth(self.left_margin_width*2.8)



    def set_image(self, image):
        height, width, channel = image.shape
        bytes_per_line = channel * width
        pixmap = QPixmap.fromImage(QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888))
        scaled_pixmap = pixmap.scaled(self.frame_label.size(), Qt.KeepAspectRatioByExpanding)

        # Calculate the dimensions to crop the center region
        x_offset = (scaled_pixmap.width() - self.frame_label.width()) // 2
        y_offset = (scaled_pixmap.height() - self.frame_label.height()) // 2

        # Crop the center region and set it as the pixmap for the frame_label
        cropped_pixmap = scaled_pixmap.copy(x_offset, y_offset+10, self.frame_label.width(), self.frame_label.height()-10)
        self.frame_label.setPixmap(cropped_pixmap)
        

    def set_crop(self, image):
        height, width, channel = image.shape
        bytes = image.tobytes()
        bytes_per_line = channel * width
        w = int(self.eyecrop_label.width() * 0.8)
        h = int(self.eyecrop_label.height() * 0.8)
        q_image = QImage(bytes, width, height, bytes_per_line, QImage.Format_RGB888)
        q_pixmap = QPixmap.fromImage(q_image)
        if not q_pixmap.isNull():
            self.eyecrop_label.setAlignment(Qt.AlignCenter)
            self.eyecrop_label.setPixmap(q_pixmap.scaled(w, h, aspectRatioMode=Qt.KeepAspectRatio))

    def showGaze(self, gaze, block):
        hori = gaze.horizontal_ratio()
        verti = gaze.vertical_ratio()
        blink = -1
        if (gaze.pupils_located):
            blink = (gaze.eye_left.blinking+gaze.eye_right.blinking)/2
           
        if hori is not None:
            self.explanation_labels[0].setText("Horizontal: {:.2f}".format(hori))
        if verti is not None:
            self.explanation_labels[1].setText("Vertical:   {:.2f}".format(verti))
        if blink is not None and blink != -1:
            blink_symbol = "O" if blink > 3.8 else "X"
            self.explanation_labels[2].setText("Blinking:   {:.2f}".format(blink))
        
        if block != 0:
            color = self.color_list[block-1] if block != 5 else (0, 0, 0)
            text = f"Looking at <span style='color: rgb{color};'>{block}</span>"
            self.current.setText(text)

        if self.verbose and gaze.pupils_located :
            left = gaze.pupil_left_coords()
            right = gaze.pupil_right_coords()

            label_width = 20  # Adjust the width as needed

            self.explanation_labels2_2[0].setText("{:.2f}".format(left[0]))
            self.explanation_labels2_2[1].setText("{:.2f}".format(left[1]))

            self.explanation_labels2_2[2].setText("{:.2f}".format(right[0]))
            self.explanation_labels2_2[3].setText("{:.2f}".format(right[1]))

            left_origin = gaze.eye_left.origin
            right_origin = gaze.eye_right.origin

            self.explanation_labels2_2[4].setText("{:.2f}".format(left_origin[0]))
            self.explanation_labels2_2[5].setText("{:.2f}".format(left_origin[1]))

            self.explanation_labels2_2[6].setText("{:.2f}".format(right_origin[0]))
            self.explanation_labels2_2[7].setText("{:.2f}".format(right_origin[1]))

            left_relative = gaze.eye_left.pupil
            right_relative = gaze.eye_right.pupil

            self.explanation_labels2_2[8].setText("{:.2f}".format(left_relative.x))
            self.explanation_labels2_2[9].setText("{:.2f}".format(left_relative.y))

            self.explanation_labels2_2[10].setText("{:.2f}".format(right_relative.x))
            self.explanation_labels2_2[11].setText("{:.2f}".format(right_relative.y))

            left_center = gaze.eye_left.center
            right_center = gaze.eye_right.center

            self.explanation_labels2_2[12].setText("{:.2f}".format(left_center[0]))
            self.explanation_labels2_2[13].setText("{:.2f}".format(left_center[1]))

            self.explanation_labels2_2[14].setText("{:.2f}".format(right_center[0]))
            self.explanation_labels2_2[15].setText("{:.2f}".format(right_center[1]))

            

        
    def showTouch(self, block):
        if block != None:
            self.formerBlock = block
            # self.current.setText("Touched "+str(block))
            color = self.color_list[block-1] if block != 5 else (0, 0, 0)
            text = f"Touched <span style='color: rgb{color};'>{block}</span>"
            self.current.setText(text)
        else: #So that former choice is displayed
            block = self.formerBlock
        

    def showTarget(self, target):
        if target != None:
            self.turn_off_all_box()
            self.set_box_visibility(target-1, True)
            color = self.color_list[target-1]
            text = f"Target is <span style='color: rgb{color};'>{target}</span>"
            self.target.setText(text)


    def showSuccess(self):
        return

    def showLoading(self, patience, max_patience):
        progress = int(patience / max_patience * 100)
        self.progress_bar.setValue(progress)
    
    def showMode(self, method, mode):
        if method == "Off":
            self.showOff()
            return
        text = f"<span style='color: #FFC701;'>{mode} Mode</span><br><span style='color: #808080;'>with {method}</span>"
        self.mode_label.setText(text)

    def set_box_visibility(self, index, visible):
        if 0 <= index < len(self.boxes):
            box = self.boxes[index]
            rgb = self.color_list[index]
            if visible:
                color = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 100)"
                box.setStyleSheet(f"background-color: {color};")
            else:
                color = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0)"
                box.setStyleSheet(f"background-color: {color};")

    def turn_off_all_box(self):
        for index in range(len(self.boxes)):
            self.set_box_visibility(index, False)

    def keyPressEvent(self, e):
        self.key_recent = e.key()
        self.key_set = True

    def resizeEvent(self, event):

        if self.verbose:
            self.left_margin_width = self.main_widget.width() // 5
            self.left_margin_widget.setFixedWidth(self.left_margin_width)
            self.frame_widget.setFixedWidth(self.left_margin_width*2.7)
            self.right_margin_widget.setFixedWidth(self.left_margin_width)
            self.progress_bar.setFixedWidth(self.left_margin_width-40)
            self.eyecrop_label.setFixedWidth(self.left_margin_width-40)


        else:
            self.left_margin_width = self.main_widget.width() // 4
            self.left_margin_widget.setFixedWidth(self.left_margin_width)
            self.frame_widget.setFixedWidth(self.left_margin_width*2.8)
            self.progress_bar.setFixedWidth(self.left_margin_width-40)
            self.eyecrop_label.setFixedWidth(self.left_margin_width-40)



        # Update the logo_label size when the left_margin_widget is resized
        w = int(self.left_margin_width)
        h = int(self.logo_pixmap.height() / 1.5)
        self.logo_label.setPixmap(self.logo_pixmap.scaled(w, h, aspectRatioMode=Qt.KeepAspectRatio))

    def showOff(self):
        text = f"<span style='color: #FFC701;'>OFF</span><br><span style='color: #808080;'>Please turn on </span><br>to use</span>"
        self.mode_label.setText(text)
        self.turn_off_all_box()
        no_signal = np.array(Image.open("./images/no_signal.png"))
        self.set_image(no_signal)






