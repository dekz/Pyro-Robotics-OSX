""" Device for getting a frequence and turning it into distance. """

import ossaudiodev, struct, math, FFT, Numeric, time, random
from pyrobot.robot.device import Device

class FrequencyDevice(Device):
    def __init__(self, dev = "/dev/dsp", sampleTime = 1.0, fake = 0):
        """
        This is an async device with no update(). 
        dev: sound card device name
        sampleTime: time, in seconds, in which to sample
        """
        Device.__init__(self, "frequency")
        self.fake = fake
        self.deviceName = dev
        self.status = "closed"
        self.number_of_channels= 1
        self.sample_rate= 14400
        self.sample_width= 1
        self.format = ossaudiodev.AFMT_U8
        self.sampleTime = sampleTime
        self.results = [1]*6
        self.lastFreq = int(self.sample_rate * self.sampleTime/ 2.0)
        self.setAsync(1)

    def setSampleTime(self, value):
        self.sampleTime = value
        self.lastFreq = int(self.sample_rate * self.sampleTime/ 2.0)
        if self.window != 0:
            self.window.updateWidget("timestamp", self.timestamp)

    def update(self):
        if not self.active: return
        self.results = self.getFreq(self.sampleTime)

    def initialize(self, mode):
        if not self.fake:
            self.dev = ossaudiodev.open(self.deviceName, mode)
            self.dev.setparameters(self.format,
                                   self.number_of_channels,
                                   self.sample_rate)
        self.status = mode
        
    def playTone(self, freq, seconds):
        """ freq example: 550 = middle C """
        if self.status != "w":
            self.initialize("w")
        sample = [128] * int(self.sample_rate * seconds)
        if type(freq) == type(1):
            freq = [freq]
        freqPortion = 127.0 / len(freq)
        for f in freq:
            for n in range(len(sample)):
                sample[n] += int(freqPortion * math.sin(n * 2 * math.pi * f/self.sample_rate))
        if self.fake: return
        self.dev.write("".join(map(chr,sample)))
        self.dev.flush()

    def read(self, seconds):
        if self.status != "r":
            self.initialize("r")
        if self.fake:
            buffer = []
            return None
        else:
            buffer = self.dev.read(int(self.sample_rate * seconds))
            size = len(buffer)
            return struct.unpack(str(size) + "B", buffer)

    def getFreq(self, seconds):
        if self.fake:
            base = 300
            if random.random() < .2:
                freq = base + randint(-50,50)
            else:
                freq = base + randint(-200, 200)
            #freq = (random.random() * 400) + 100.0
            distance = freq * 0.0051 - 0.0472
            return (distance, freq, 1, 1, 1, 1)
        data = self.read(seconds)
        self.timestamp = time.time()
        transform = FFT.real_fft(data).real
        minFreq = 20 
        maxFreq = 700
        minFreqPos = int(minFreq * seconds)
        maxFreqPos = int(maxFreq * seconds)
        minFreqPos = max(0, minFreqPos)
        maxFreqPos = min(int(self.sample_rate * seconds), maxFreqPos)
        if minFreqPos == maxFreqPos:
            self.lastFreq = int(self.sample_rate * sampleTime/ 2.0)
            return
        elif minFreqPos > maxFreqPos:
            minFreqPos, maxFreqPos = maxFreqPos, minFreqPos
        freqPos = Numeric.argmax(transform[1+minFreqPos:maxFreqPos])
        value = transform[1+minFreqPos:maxFreqPos][freqPos]
        freq = int((freqPos + minFreqPos) / seconds)
        distance = freq * 0.0051 - 0.0472
        bestFreqPos = Numeric.argmax(transform[1:])
        bestValue = transform[1:][bestFreqPos]
        bestFreq = int(bestFreqPos / seconds)
        return (distance, freq, value, transform[0], bestFreq, bestValue)

    def close(self):
        if self.status != "closed":
            if not self.fake:
                self.dev.close()
            self.status = "closed"

    def addWidgets(self, window):
        """Method to addWidgets to the device window."""
        freq, bestAmt, totalAmt = [1] * 3
        try:
            distance, freq, bestAmt, totalAmt, overallBest, overallAmt = self.results
        except: pass
        window.addData("distance", "distance:", distance)
        window.addData("freqency", "frequency:", freq)
        window.addData("ratio", "percentage:", float(bestAmt)/totalAmt)
        window.addData("overallbest", "overall best freq:", overallBest)
        window.addData("overallbestamount", "overall best %:", float(overallAmt)/totalAmt)
        window.addData("timestamp", "timestamp:", self.timestamp)
        window.addCommand("sleep", "sleep between reads:", self.asyncSleep,
                          self.setSleep)
        window.addCommand("sample", "sample time:", self.sampleTime,
                          self.setSample)

    def updateWindow(self):
        freq, bestAmt, totalAmt = [1] * 3
        try:
            distance, freq, bestAmt, totalAmt, overallBest, overallAmt = self.results
        except: pass
        if self.window != 0:
            self.window.updateWidget("distance", distance)
            self.window.updateWidget("freqency", freq)
            self.window.updateWidget("ratio", float(bestAmt)/totalAmt)
            self.window.updateWidget("overallbest", overallBest)
            self.window.updateWidget("overallbestamount", float(overallAmt)/totalAmt)
            self.window.updateWidget("timestamp", self.timestamp)

    def setSleep(self, value):
        self.asyncSleep = float(value)

    def setSample(self, value):
        self.setSampleTime(float(value))

        
if __name__ == "__main__":
    sd = FrequencyDevice("/dev/dsp", fake =1)
    sd.playTone(770, 1)
    sd.playTone(852, 1)
    sd.getFreq(1)
    #for col in [697, 770, 852, 941]:
    #    for row in [1209, 1336, 1477, 1633]:
    #        sd.playTone((row, col), 1)

def INIT(robot):
    return {"frequency": FrequencyDevice("/dev/dsp")}
