import pygame
import pyaudio
import atexit
import sys
import wave
import struct

class ByteBeat:
    def __init__(self,func,sample_rate=8000,channels=1,buffer_size=1024,display=True,width=1024,height=256,samples_per_pixel=1):
        pygame.init()

        self.func = func
        self.sample_rate = sample_rate
        self.channels = channels
        self.buffer_size = buffer_size
        self.display = display
        self.width = width
        self.height = height
        self.samples_per_pixel = samples_per_pixel

    def save(self,path,nsamples):
        with wave.open(path,"wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(1)
            wf.setframerate(self.sample_rate)

            samples = []
            for t in range(nsamples):
                try:
                    v = self.func(t)
                    if not isinstance(v,list): v = [v]
                except:
                    v = [0] * self.channels

                v = list(map(lambda x:int(x%256), v))
                samples.extend(v)

            wf.writeframes(bytes(samples))

    def play(self,start=0):
        self.T = start
        self.scroll = 0
        
        if self.display:
            self.width = self.width
            self.height = self.height
            self.screen = pygame.display.set_mode((self.width,self.height))
            pygame.display.set_caption("bytebeat")

            icon = pygame.Surface((32,32))
            icon.set_colorkey((0,0,0))
            pygame.draw.circle(icon,(0,127,255),(15,15),15,2)
            pygame.display.set_icon(icon)

        self.p = pyaudio.PyAudio()
        self.bytes = [[-1]*(self.buffer_size*2//self.samples_per_pixel*self.samples_per_pixel) for _ in range(self.channels)]
        self.idx = 0
        
        def callback(in_data, frame_count, time_info, status):
            buf = []
            for t in range(frame_count):
                try:
                    v = self.func(self.T+t)
                    if not isinstance(v,list): v = [v]
                except:
                    v = [0] * self.channels

                v = list(map(lambda x:int(x%256), v))

                buf.extend(v)

                for i in range(self.channels):
                    self.bytes[i][self.idx] = v[i]

                self.idx += 1
                self.idx %= len(self.bytes[0])

            self.T += frame_count
                
            return (bytes(buf), pyaudio.paContinue)

        self.stream = self.p.open(
            format=pyaudio.paUInt8,
            channels=self.channels,
            rate=self.sample_rate,
            output=True,
            frames_per_buffer=self.buffer_size,
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
        premn = [0]*self.channels
        premx = [255]*self.channels

        while 1:
            dt = clock.tick(self.sample_rate)

            self.scroll += dt*self.sample_rate/1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            while self.scroll >= self.samples_per_pixel:
                self.screen.scroll(-1)

                avg = 0

                out = []

                for i in range(self.channels):
                    mn = min(self.bytes[i][idx:idx+self.samples_per_pixel])
                    mx = max(self.bytes[i][idx:idx+self.samples_per_pixel])

                    avg += sum(self.bytes[i][idx:idx+self.samples_per_pixel])//self.samples_per_pixel

                    premn[i],premx[i],mn,mx = mn,mx,min(premx[i],mn),max(premn[i],mx)
                    
                    mn = mn*self.height//256
                    mx = mx*self.height//256

                    if i == 0:
                        mn,mx = self.height - mx - 1, self.height - mn - 1

                    col = [[],[(255,255,255)],[(0,255,0),(255,0,255)]][self.channels][i]
                    out.append((mn,mx,col))

                avg //= self.channels
                if avg >= 0:
                    idx += self.samples_per_pixel
                    idx %= len(self.bytes[0])

                    self.screen.fill((0,avg//2,avg),(self.width-1,0,1,self.height))

                    for mn,mx,col in out:
                        self.screen.fill(col,(self.width-1,mn,1,mx-mn+1),special_flags=pygame.BLEND_ADD)

                self.scroll -= self.samples_per_pixel

            pygame.display.update()