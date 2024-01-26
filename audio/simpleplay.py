import simpleaudio as sa


class SimplePlay:
    def __init__(self):
        super().__init__()
        self.path = r'/home/pi/PlayEye/audio/' #set path
    

    def targetSuccess(self):
        filename = r'/success.wav'
        wave_obj = sa.WaveObject.from_wave_file(self.path + filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        
    def targetWrong(self):
        filename = r'/wrong.wav'
        wave_obj = sa.WaveObject.from_wave_file(self.path + filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        
    def stageSuccess(self):
        filename = r'/stage_clear.wav'
        wave_obj = sa.WaveObject.from_wave_file(self.path + filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    
    def modeSelect(self):
        filename = r'/mode_select.wav'
        wave_obj = sa.WaveObject.from_wave_file(self.path + filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()

    def eightMode(self):
        filename = r'/eight.wav'
        wave_obj = sa.WaveObject.from_wave_file(self.path + filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()

    def roundMode(self):
        filename = r'/round.wav'
        wave_obj = sa.WaveObject.from_wave_file(self.path + filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()

    def touchMode(self):
        filename = r'/touch.wav'
        wave_obj = sa.WaveObject.from_wave_file(self.path + filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()

    def shiftMode(self):
        filename = r'/shift.wav'
        wave_obj = sa.WaveObject.from_wave_file(self.path + filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()

    def quitMode(self):
        filename = r'/quit.wav'
        wave_obj = sa.WaveObject.from_wave_file(self.path + filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    
    def animalSound(self, idx):
        animal_list = ['elephant', 'cat', 'fish', 'pig', 'empty', 'rabbit', 'duck', 'gorilla', 'hedgehog']
        filename = r'/animal/' + animal_list[idx-1] + '.wav'
        wave_obj = sa.WaveObject.from_wave_file(self.path + filename)
        play_obj = wave_obj.play()
        play_obj.wait_done()

if __name__ == "__main__":
    print("debug for simpleplay")
    player = SimplePlay()
    player.shiftMode()
    player.targetSuccess()
    player.roundMode()
    player.targetSuccess()
    player.touchMode()
    player.targetSuccess()
    player.eightMode()
    
    for i in range(9):
        if i==4 :
            continue
        else:
            player.animalSound(i+1)
