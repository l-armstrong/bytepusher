from enum import Enum, IntEnum
import pygame

class Emulator_State(Enum):
    QUIT = 0
    RUNNING = 1
    PAUSED = 2

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
        self.mem = [0] * 16777224 # 16 MiB 
        self.pc = 0
        self.state = Emulator_State.RUNNING
        # load color
        for r in range(6):
            for g in range(6):
                for b in range(6):
                    self.colormap[r*36*g*b] = (r*0x33)<<16 | (g*0x33)<<8 | b*0x33

    def load_program(self, program):
        with open(program, "rb") as f:
            i  = 0
            while (byte := f.read(1)):
                self.mem[i] = byte
                i += 1
    
    def run(self):
        # Poll the keys and store their states as a 2-byte value at address 0.
        # Address 0; Bytes = 2; Keyboard state. Key X = bit X.
        key16 = self.mem[0] << 8 | self.mem[1]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.state = Emulator_State.QUIT
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:   key16 |= 0b0000_0000_0000_0010
                elif event.key == pygame.K_2: key16 |= 0b0000_0000_0000_0100
                elif event.key == pygame.K_3: key16 |= 0b0000_0000_0000_1000
                elif event.key == pygame.K_4: key16 |= 0b0001_0000_0000_0000

                elif event.key == pygame.K_q: key16 |= 0b0000_0000_0001_0000
                elif event.key == pygame.K_w: key16 |= 0b0000_0000_0010_0000
                elif event.key == pygame.K_e: key16 |= 0b0000_0000_0100_0000
                elif event.key == pygame.K_r: key16 |= 0b0010_0000_0000_0000
                
        # Fetch the 3-byte program counter from address 2, and execute exactly 65536 instructions.

        # Send the 64-KiB pixeldata block designated by the byte value at address 5 to the display device.

        # Send the 256-byte sampledata block designated by the 2-byte value at address 6 to the audio device.


    

if __name__ == '__main__':
    config = Config()
    bytepusher = BytePusher()
    bytepusher.load_program("PaletteTest.BytePusher")
    pygame.init()

    while bytepusher.state == Emulator_State.RUNNING: 
        pass
