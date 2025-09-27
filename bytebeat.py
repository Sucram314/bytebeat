import pygame
import pyaudio
import atexit
import sys

class ByteBeat:
    def __init__(self,func,start=0,sample_rate=8000,channels=1,format=pyaudio.paUInt8,buffer_size=1024,display=True,width=1024,height=256,samples_per_pixel=1):
        pygame.init()

        self.T = start
        self.scroll = 0
        
        self.display = display
        if self.display:
            self.width = width
            self.height = height
            self.screen = pygame.display.set_mode((width,height))
            pygame.display.set_caption("bytebeat")

            icon = pygame.Surface((32,32))
            icon.set_colorkey((0,0,0))
            pygame.draw.circle(icon,(0,127,255),(15,15),15,2)
            pygame.display.set_icon(icon)

        self.p = pyaudio.PyAudio()
        self.bytes = [-1]*(buffer_size*2//samples_per_pixel*samples_per_pixel)
        self.idx = 0
        
        def callback(in_data, frame_count, time_info, status):
            buf = []
            for t in range(frame_count):
                try:
                    v = func(self.T+t)
                except:
                    v = 0

                v = int(v%256)

                buf.append(v)
                self.bytes[self.idx] = v
                self.idx += 1
                self.idx %= len(self.bytes)

            self.T += frame_count
                
            return (bytes(buf), pyaudio.paContinue)

        self.stream = self.p.open(
            format=format,
            channels=channels,
            rate=sample_rate,
            output=True,
            frames_per_buffer=buffer_size,
            stream_callback=callback
        )

        def close():
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            pygame.quit()

        atexit.register(close)

        clock = pygame.time.Clock()

        idx = 0
        premn = 0
        premx = 255

        while 1:
            dt = clock.tick(sample_rate)

            self.scroll += dt*sample_rate/1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            while self.scroll >= samples_per_pixel:
                mn = min(self.bytes[idx:idx+samples_per_pixel])
                mx = max(self.bytes[idx:idx+samples_per_pixel])

                if 0 <= mn <= mx:
                    self.screen.scroll(-1)

                    avg = sum(self.bytes[idx:idx+samples_per_pixel])//samples_per_pixel
                    
                    idx += samples_per_pixel
                    idx %= len(self.bytes)

                    premn,premx,mn,mx = mn,mx,min(premx,mn),max(premn,mx)

                    self.screen.fill((0,avg//2,avg),(self.width-1,0,1,self.height))
                    mn = self.height - mn*self.height//256 - 1
                    mx = self.height - mx*self.height//256 - 1
                    self.screen.fill((255,255,255),(self.width-1,mx,1,mn-mx+1))

                self.scroll -= samples_per_pixel

            pygame.display.update()