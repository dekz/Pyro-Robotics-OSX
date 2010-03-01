try:
    import ossaudiodev
except:
    print "ossaudiodev not installed"
    ossaudiodev = None
try:
    import FFT
except:
    print "FFT not installed"
    ossaudiodev = None
try:
    import Numeric
except:
    print "Numeric not installed"
    ossaudiodev = None
import struct, math, time, threading, copy

def add(s1, s2):
    return minmax([(v1 + v2) for (v1, v2) in zip(s1, s2)])

def minmax(vector):
    return [min(max(v,0),255) for v in vector]

def scale(sample, value):
    return minmax([((s - 128) * value) + 128 for s in sample])

def sine(freqs, seconds, volume = 1.0, sample_rate = 8000.0):
    sample = [128] * int(sample_rate * seconds)
    if type(freqs) == type(0):
        freqs = [freqs]
    for freq in freqs:
        for n in range(len(sample)):
            sample[n] += int(127 * math.sin(n * 2 * math.pi * freq/sample_rate) * volume)
    return minmax(sample)

class SoundThread(threading.Thread):
    def __init__(self, parent, name = "sound thread"):
        threading.Thread.__init__(self, name = name)
        self.parent = parent
        self.event  = threading.Event()
        self.start()
    def run(self):
        while not self.event.isSet():
            self.parent.lock.acquire()
            buffer = copy.copy(self.parent.buffer)
            self.parent.buffer = None
            self.parent.lock.release()
            if buffer != None:
                self.parent.dev.write("".join(map(chr,buffer)))
                self.parent.dev.flush()
            self.event.wait(.001)
    def join(self, timeout=None):
        self.event.set()
        threading.Thread.join(self, timeout)
            
class SoundDevice:
    def __init__(self, device, async = 0, cache = 1):
        self.device = device
        self.async = async
        self.cache = cache
        self.cacheDict = {}
        self.status = "closed"
        self.number_of_channels= 1
        self.sample_rate= 8000
        self.sample_width= 1
        self.minFreq = 20
        self.maxFreq = 3500
        self.debug = 0
        self.buffer = None
        if ossaudiodev != None:
            self.format = ossaudiodev.AFMT_U8
            if self.debug:
                self.setFile("770.txt")
            if self.async:
                self.lock = threading.Lock()
                self.thread = SoundThread(self)

    def initialize(self, mode):
        if ossaudiodev == None: return
        self.dev = ossaudiodev.open("/dev/dsp", mode)
        self.dev.setparameters(self.format,
                              self.number_of_channels,
                              self.sample_rate)
        self.status = mode

    def play(self, sample):
        """
        """
        if ossaudiodev == None: return
        if self.status != "w":
            self.initialize("w")
        if self.async:
            self.lock.acquire()
            self.buffer = sample
            self.lock.release()
        else:
            self.dev.write("".join(map(chr,sample)))
            self.dev.flush()
        
    def playTone(self, freqs, seconds, volume = 1.0):
        """
        freq example: playTone([550,400], .1, volume=.5) # middle C for .1 seconds, half volume
        """
        if ossaudiodev == None: return
        if type(freqs) == type(0):
            freqs = [freqs]
        if self.status != "w":
            self.initialize("w")
        sample = [128] * int(self.sample_rate * seconds)
        for freq in freqs:
            if self.cache and (freq,seconds) in self.cacheDict:
                sample = self.cacheDict[(freq,seconds)]
            else:
                for n in range(len(sample)):
                    sample[n] = min(max(sample[n] + int(127 * math.sin(n * 2 * math.pi * freq/self.sample_rate) * volume), 0),255)
                self.cacheDict[(freq,seconds)] = sample
        if self.async:
            self.lock.acquire()
            self.buffer = sample
            self.lock.release()
        else:
            self.dev.write("".join(map(chr,sample)))
            self.dev.flush()

    def read(self, seconds):
        if ossaudiodev == None: return
        if self.status != "r":
            self.initialize("r")
        buffer = self.dev.read(int(self.sample_rate * seconds))
        size = len(buffer)
        return struct.unpack(str(size) + "B", buffer)

    def setFile(self, filename):
        if ossaudiodev == None: return
        self.filename = filename
        self.fp = open(self.filename, "r")

    def readFile(self, seconds):
        if ossaudiodev == None: return
        data = None
        try:
            data = eval(self.fp.readline())
        except:
            self.fp = open(self.filename, "r")
            try:
                data = eval(self.fp.readline())
            except:
                print "Failed reading file '%s'" % self.filename
        time.sleep(seconds)
        return data[:int(seconds * self.sample_rate)]

    def getFreq(self, seconds):
        # change to read from the buffer, rather than block
        if ossaudiodev == None: return
        if self.debug:
            data = self.readFile(1)
        else:
            data = self.read(seconds)
        transform = FFT.real_fft(data).real
        minFreqPos = self.minFreq
        maxFreqPos = self.maxFreq
        freq = Numeric.argmax(transform[1+minFreqPos:maxFreqPos])
        value = transform[1+minFreqPos:maxFreqPos][freq]
        domFreq = (freq + self.minFreq) / seconds
        if self.debug and abs(value) > 8000 and self.minFreq < domFreq < self.maxFreq:
            print "Frequence:", domFreq, "Value:", value, "Volume:", transform[0]
        return (domFreq, value, transform[0])

    def close(self):
        if ossaudiodev == None: return
        if self.status != "closed":
            self.dev.close()
            self.status = "closed"

if __name__ == "__main__":
    sd = SoundDevice("/dev/dsp", async = 1)
    sd.playTone(500, 1)
        
## DTMF Tones

##                  1209 Hz 1336 Hz 1477 Hz 1633 Hz

##                           ABC     DEF
##    697 Hz          1       2       3       A

##                   GHI     JKL     MNO
##    770 Hz          4       5       6       B

##                   PRS     TUV     WXY
##    852 Hz          7       8       9       C

##                           oper
##    941 Hz          *       0       #       D


