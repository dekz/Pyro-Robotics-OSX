import RandomArray
import Numeric
import operator

def randomBits(length):
    address = RandomArray.randint(0, 2, length)
    return address

def rnd3(val):
    if val == 0: return 0
    if val > 0: return 1
    return -1

def rnd2(val):
    if val > 0: return 1
    return -1

class Neuron:

    def __init__(self, address):
        self.address = address

    def distance(self, otherAddress):
        xor = Numeric.logical_xor(self.address, otherAddress)
        sum = reduce( operator.add, xor)
        return sum

    def select(self, otherAddress, threshold):
        return self.distance(otherAddress) >= threshold

#----------------------------------------------------------------

class HardLocation:

    def __init__(self, addressLength, dataLength):
        self.addressDecoder = Neuron(randomBits(addressLength))
        self.counters = Numeric.zeros(dataLength)

    def select(self, address, threshold):
        return self.addressDecoder.select(address, threshold)

    def distance(self, address):
        return self.addressDecoder.distance(address)

#----------------------------------------------------------------

class SDM:

    def __init__(self, addressLength = 1000, dataLength = 10,
                 memorySize = 1000, threshold = None, verbose = 0):
        self.verbose = verbose
        if verbose: print "Creating SDM..."
        self.addressLength = addressLength
        self.dataLength = dataLength
        self.memorySize = memorySize
        if threshold == None:
            self.threshold = addressLength / 2
        else:
            self.threshold = threshold
        self.memory = [HardLocation(addressLength, dataLength)
                       for i in range(memorySize)]
        if verbose: print "Done!"

    def select(self, address, threshold = None):
        if threshold == None: threshold = self.threshold
        if self.verbose: print "threshold = %d" % threshold,
        retval = map(lambda m: HardLocation.select(m, address, threshold),
                     self.memory)
        return retval

    def read(self, address, threshold = None):
        if self.verbose: print "Reading...",
        s = self.select( address, threshold)
        counts = Numeric.zeros( self.dataLength)
        for i in range(len(s)):
            if s[i]:
                counts += self.memory[i].counters
        if self.verbose: print "done!"
        return [rnd3(x) for x in counts]

    def write(self, address, data, threshold = None):
        if self.verbose: print "Writing", data,
        s = self.select( address, threshold)
        for i in range(len(s)):
            if s[i]:
                self.memory[i].counters += data
        if self.verbose: print "done!"
        return "ok"
                
    def distance(self, address):
        retval = map(lambda m: HardLocation.distance(m, address),
                     self.memory)
        return retval

if __name__ == '__main__':

    sdm = SDM(verbose = 1)
    ra = randomBits(sdm.addressLength)
    #print sdm.distance(ra)
    #print sdm.select(ra)
    print sdm.read(ra)
    print sdm.write(ra, map(rnd2, randomBits(sdm.dataLength)))
    print sdm.read(ra)
