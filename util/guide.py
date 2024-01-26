import random
class EyeGuide(object):
    def __init__(self):
        self.rotation_set = {"Round":[1,2,3,6,9,8,7,4], "Eight":[1,2,3,5,7,8,9], "Shift":[1,9,3,7,6,4,2,8]}
        self.prev = 5
        self.mode = None
    
    def setMode(self, mode):
        self.mode = mode

    def getMode(self):
        return self.mode

    def getTarget(self):
        if self.mode == "Random":
            target = []
            num = random.randint(1, 9)
            while (num == 5 or num == self.prev):
                num = random.randint(1, 9)
            
            target.append(num)
            self.prev = num
            return target
        else:
            return self.rotation_set[self.mode]
    
        