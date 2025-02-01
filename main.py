from enum import Enum
import pygame
import numpy as np 

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
        # self.mem = [0] * 16777224 # 16 MiB 
        self.mem = bytearray(16777224) # 16 MiB 
        # self.mem = np.zeros(16777224, dtype=np.uint8) # 16 MiB 
        self.pc = 0
        self.state = Emulator_State.RUNNING
        # load color
        for r in range(6):
            for g in range(6):
                for b in range(6):
                    self.colormap[r*36+g*6+b] = (r*0x33)<<16 | (g*0x33)<<8 | b*0x33

    def load_program(self, program):
        with open(program, "rb") as f:
            i  = 0
            while (byte := f.read(1)):
                self.mem[i] = int.from_bytes(byte, byteorder="big")
                i += 1
    
    def run(self):
        # Poll the keys and store their states as a 2-byte value at address 0.
        # Address 0; Bytes = 2; Keyboard state. Key X = bit X.
        key16 = self.mem[0] << 8 | self.mem[1]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:self.state = Emulator_State.QUIT;return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:self.state = Emulator_State.QUIT;return
                elif event.key == pygame.K_1:   key16 |= 0b0000_0000_0000_0010
                elif event.key == pygame.K_2: key16 |= 0b0000_0000_0000_0100
                elif event.key == pygame.K_3: key16 |= 0b0000_0000_0000_1000
                elif event.key == pygame.K_4: key16 |= 0b0001_0000_0000_0000

                elif event.key == pygame.K_q: key16 |= 0b0000_0000_0001_0000
                elif event.key == pygame.K_w: key16 |= 0b0000_0000_0010_0000
                elif event.key == pygame.K_e: key16 |= 0b0000_0000_0100_0000
                elif event.key == pygame.K_r: key16 |= 0b0010_0000_0000_0000

                elif event.key == pygame.K_a: key16 |= 0b0000_0000_1000_0000
                elif event.key == pygame.K_s: key16 |= 0b0000_0001_0000_0000
                elif event.key == pygame.K_d: key16 |= 0b0000_0010_0000_0000
                elif event.key == pygame.K_f: key16 |= 0b0100_0000_0000_0000

                elif event.key == pygame.K_z: key16 |= 0b0000_0100_0000_0000
                elif event.key == pygame.K_x: key16 |= 0b0000_0000_0000_0001
                elif event.key == pygame.K_c: key16 |= 0b0000_1000_0000_0000
                elif event.key == pygame.K_v: key16 |= 0b1000_0000_0000_0000
            elif event.type == pygame.key:
                if event.key == pygame.K_1:   key16 &= ~(0b0000_0000_0000_0010)
                elif event.key == pygame.K_2: key16 &= ~(0b0000_0000_0000_0100)
                elif event.key == pygame.K_3: key16 &= ~(0b0000_0000_0000_1000)
                elif event.key == pygame.K_4: key16 &= ~(0b0001_0000_0000_0000)

                elif event.key == pygame.K_q: key16 &= ~(0b0000_0000_0001_0000)
                elif event.key == pygame.K_w: key16 &= ~(0b0000_0000_0010_0000)
                elif event.key == pygame.K_e: key16 &= ~(0b0000_0000_0100_0000)
                elif event.key == pygame.K_r: key16 &= ~(0b0010_0000_0000_0000)

                elif event.key == pygame.K_a: key16 &= ~(0b0000_0000_1000_0000)
                elif event.key == pygame.K_s: key16 &= ~(0b0000_0001_0000_0000)
                elif event.key == pygame.K_d: key16 &= ~(0b0000_0010_0000_0000)
                elif event.key == pygame.K_f: key16 &= ~(0b0100_0000_0000_0000)

                elif event.key == pygame.K_z: key16 &= ~(0b0000_0100_0000_0000)
                elif event.key == pygame.K_x: key16 &= ~(0b0000_0000_0000_0001)
                elif event.key == pygame.K_c: key16 &= ~(0b0000_1000_0000_0000)
                elif event.key == pygame.K_v: key16 &= ~(0b1000_0000_0000_0000)

        self.mem[0] = key16 >> 8
        self.mem[1] = key16 & 0xFF
        # Fetch the 3-byte program counter from address 2, and execute exactly 65536 instructions.
        pc = (self.mem[2] << 16) | (self.mem[3] << 8) | self.mem[4]
        for _ in range(65536):
            dst = (self.mem[pc+3] << 16) | (self.mem[pc+4] << 8) | (self.mem[pc+5])
            src = (self.mem[pc] << 16) | (self.mem[pc+1] << 8) | (self.mem[pc+2])
            self.mem[dst] = self.mem[src]
            pc = (self.mem[pc+6] << 16) | (self.mem[pc+7] << 8) | (self.mem[pc+8])

        # Send the 64-KiB pixeldata block designated by the byte value at address 5 to the display device.
        pixel_data_i = self.mem[5] << 16
        for i in range(len(self.display)):
            self.display[i] = self.colormap[self.mem[pixel_data_i]]
            pixel_data_i += 1
        # Send the 256-byte sampledata block designated by the 2-byte value at address 6 to the audio device

if __name__ == '__main__':
    config = Config()
    bytepusher = BytePusher()
    bytepusher.load_program("ScrollingLogo.BytePusher")
    pygame.init()
    screen = pygame.display.set_mode((config.width, config.height))
    pixels = pygame.PixelArray(screen)
    clock = pygame.time.Clock()

    while bytepusher.state == Emulator_State.RUNNING: 
        screen.fill((0, 0, 0))
        bytepusher.run()
        for i in range(len(bytepusher.display)):
            x = i % 256
            y = i // 256
            pixels[x, y] = bytepusher.display[i]
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()