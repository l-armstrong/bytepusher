import pygame

class Config(object):
    def __init__(self, scale=3):
        self.width = 256
        self.height = 256
        self.scale = scale

class BytePusher(object):
    def __init__(self):
        self.display = [0] * (256*256) # 	256*256 pixels, 1 byte per pixel, 216 fixed colors
        self.colormap = [0] * 256
        self.keypad = [False] * 16
        self.ram = [0] * 16777224 # 16 MiB 
        self.pc = 0
        # load color
        for r in range(6):
            for g in range(6):
                for b in range(6):
                    self.colormap[r*36*g*b] = (r*0x33)<<16 | (g*0x33)<<8 | b*0x33

    def load_program(self, program):
        with open(program, "rb") as f:
            i  = 0
            while (byte := f.read(1)):
                self.ram[i] = byte
                i += 1
    

if __name__ == '__main__':
    config = Config()
    bytepusher = BytePusher()
    bytepusher.load_program("PaletteTest.BytePusher")
    pygame.init()