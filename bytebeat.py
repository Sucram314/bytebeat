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
        self.bytes = [[-1]*(buffer_size*2//samples_per_pixel*samples_per_pixel) for _ in range(channels)]
        self.idx = 0
        
        def callback(in_data, frame_count, time_info, status):
            buf = []
            for t in range(frame_count):
                try:
                    v = func(self.T+t)
                    if not isinstance(v,list): v = [v]
                except:
                    v = [0] * channels

                v = list(map(lambda x:int(x%256), v))

                buf.extend(v)

                for i in range(channels):
                    self.bytes[i][self.idx] = v[i]

                self.idx += 1
                self.idx %= len(self.bytes[0])

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
        premn = [0]*channels
        premx = [255]*channels

        while 1:
            dt = clock.tick(sample_rate)

            self.scroll += dt*sample_rate/1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            while self.scroll >= samples_per_pixel:
                self.screen.scroll(-1)

                avg = 0

                out = []

                for i in range(channels):
                    mn = min(self.bytes[i][idx:idx+samples_per_pixel])
                    mx = max(self.bytes[i][idx:idx+samples_per_pixel])

                    avg += sum(self.bytes[i][idx:idx+samples_per_pixel])//samples_per_pixel

                    premn[i],premx[i],mn,mx = mn,mx,min(premx[i],mn),max(premn[i],mx)
                    
                    mn = mn*self.height//256
                    mx = mx*self.height//256

                    if i == 0:
                        mn,mx = self.height - mx - 1, self.height - mn - 1

                    col = [[],[(255,255,255)],[(0,255,0),(255,0,255)]][channels][i]
                    out.append((mn,mx,col))

                avg //= channels
                if avg >= 0:
                    idx += samples_per_pixel
                    idx %= len(self.bytes[0])

                    self.screen.fill((0,avg//2,avg),(self.width-1,0,1,self.height))

                    for mn,mx,col in out:
                        self.screen.fill(col,(self.width-1,mn,1,mx-mn+1),special_flags=pygame.BLEND_ADD)

                self.scroll -= samples_per_pixel

            pygame.display.update()