import board
import time
import neopixel
import simpleaudio as sa

class LED():
    def __init__(self):
        self.num_pixels = 16
        self.pixels = neopixel.NeoPixel(board.D18, self.num_pixels)
        self.rotation_set = {"Round":[1,2,3,6,9,8,7,4], "Eight":[1,2,3,5,7,8,9], "Shift":[1,9,3,7,6,4,2,8]}

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
        self.led_dict = { 1:0, 2:1, 3:2, 4:7, 5:0, 6:3, 7:6, 8:5, 9:4}

    def light_on(self, index):
        index = self.led_dict[index]
        color = self.color_list[index]
        self.pixels[index*2+1] = color
        self.pixels[index*2] = color

    def light_on_color(self, index, color_index):
        index = self.led_dict[index]
        color_index = self.led_dict[color_index]
        color = self.color_list[color_index]
        self.pixels[index*2+1] = color
        self.pixels[index*2] = color
    
    def light_off(self, index):
        index = self.led_dict[index]
        self.pixels[index*2+1] = (0, 0, 0)
        self.pixels[index*2] =(0, 0, 0)
    
    def light_all_on(self):
        for i in range(9):
            if i != 4:
                self.light_on(1+i)
    
    def light_all_white(self):
        for i in range(8):
                self.pixels[i*2+1] = (255, 255, 255)
                self.pixels[i*2] = (255, 255, 255)

    def light_all_off(self):
        for i in range(9):
            if i != 4:
                self.light_off(1+i)

    def showMode(self, mode):
        if mode == "Random":
            self.light_on(1)
            self.light_on(2)
            self.light_on(3)
            time.sleep(0.3)
            self.light_off(1)
            self.light_off(2)
            self.light_off(3)
            self.light_on(4)
            self.light_on(6)
            time.sleep(0.3)
            self.light_off(4)
            self.light_off(6)
            self.light_on(7)
            self.light_on(8)
            self.light_on(9)
            time.sleep(0.3)
            self.light_off(7)
            self.light_off(8)
            self.light_off(9)
        else:
            order = self.rotation_set[mode]
            for i in order:
                self.light_on(i)
                time.sleep(0.15)
                self.light_off(i)


    def showNear(self, b, b1, b2, b3, b4, b5, b6, b7):
        self.light_on_color(b1, b)
        self.light_on_color(b2, b)
        time.sleep(0.15)
        self.light_off(b1)
        self.light_off(b2)
        self.light_on_color(b3, b)
        self.light_on_color(b4, b)
        time.sleep(0.15)
        self.light_off(b3)
        self.light_off(b4)
        self.light_on_color(b5, b)
        self.light_on_color(b6, b)
        self.light_on_color(b7, b)
        time.sleep(0.15)
        self.light_off(b5)
        self.light_off(b6)
        self.light_off(b7)


    def showTouch(self, block):
        if block == 1:
            self.showNear(1, 2, 4, 3, 7, 8, 6, 9)
        elif block == 2:
            self.showNear(2, 1, 3, 4, 6, 9, 7, 8)
        elif block == 3:
            self.showNear(3, 2, 6, 1, 9, 4, 8, 7)
        elif block == 4:
            self.showNear(4, 1, 7, 2, 8, 3, 9, 6)
        elif block == 6:
            self.showNear(6, 3, 9, 2, 8, 1, 4, 7)
        elif block == 7:
            self.showNear(7, 4, 8, 1, 9, 2, 3, 6)
        elif block == 8:
            self.showNear(8, 7, 9, 4, 6, 1, 2, 3)
        elif block == 9:
            self.showNear(9, 8, 6, 7, 3, 1, 2, 4)

    def showWrongTouch(self, block):
        self.light_on_color(block, 1)
        time.sleep(0.05)
        self.light_off(block)
        time.sleep(0.05)
        self.light_on_color(block, 1)
        time.sleep(0.05)
        self.light_off(block)
        time.sleep(0.05)
        self.light_on_color(block, 1)
        time.sleep(0.05)
        self.light_off(block)
        time.sleep(0.05)
        
if __name__ == "__main__":
    led = LED()
    led.light_all_white()
