"""
evolang.py for exploring ideas from:
Emergence of Communication in Teams of Embodied and Situated
Agents, by Davide Marocco and Stefano Nolfi, ALife 2006.

Author: Doug Blank
        Bryn Mawr College
Date:   March 2008

For use with PyroRobotics.org
"""

from pyrobot.simulators.pysim import *
from pyrobot.geometry import distance, Polar
from pyrobot.tools.sound import SoundDevice
from pyrobot.brain.ga import *
from pyrobot.robot.symbolic import Simbot
from pyrobot.engine import Engine
from pyrobot.brain import Brain
from pyrobot.brain.conx import SRN
import sys, time, random, math

############################################################
# First, let's define the brains to be used by each robot:
############################################################
class NNBrain(Brain):
    def setup(self):
        self.robot.range.units = "scaled"
        self.net = SRN()
        self.sequenceType = "ordered-continuous"
        # INPUT: ir, ears, mouth[t-1]
        #        sonar, stall, ears, eyes, speech[t-1]
        self.net.addLayer("input", len(self.robot.range) + 1 + 4 + 1 + 1) 
        self.net.addContextLayer("context", 2, "hidden")
        self.net.addLayer("hidden", 2)
        # OUTPUT: trans, rotate, say
        self.net.addLayer("output", 3)
        # ----------------------------------
        self.net.connect("input", "output")
        self.net.connect("input", "hidden")
        self.net.connect("context", "hidden")
        self.net.connect("hidden", "output")
        self.net["context"].setActivations(.5)
        self.net.learning = 0

    def step(self, ot1, or1):
        t, r = [((v * 2) - 1) for v in [ot1, or1]]
        self.robot.move(t, r)
        
    def propagate(self, sounds):
        light = [max(map(lambda v: math.floor(v),self.robot.light[0].values()))]
        inputs = (self.robot.range.distance() + [self.robot.stall] + 
                  sounds + light + [self.net["output"].activation[2]])
        self.net.propagate(input=inputs)
        self.net.copyHiddenToContext()
        return [v for v in self.net["output"].activation] # t, r, speech

# Defaults:
SimulatorClass, PioneerClass = TkSimulator, TkPioneer
robotCount = 4
automaticRestart = False
sd = "/dev/dsp"
startEvolving = False
loadPop = None
numTrials = 5
numSeconds = 30
numPopsize= 30
numMaxgen = 100
canHear = True
# Robot colors; make sure you have enough for robotCount:
colors = ["red", "blue", "green", "purple", "pink", "orange", "white"]

i = 1
while i < len(sys.argv):
    if sys.argv[i] == "-h":
        print "python evolang.py command line:"
        print 
        print "   -g 2d|3d|none  (graphics, default 2d)"
        print "   -n N           (robot count, default 4)"
        print "   -a             (automatic restart, default off)"
        print "   -e             (start evolving, default off)"
        print "   -p /dev/dsp    (sound device or none, default /dev/dsp)"
        print "   -l file.pop    (load a population of genes)"
        print "   -t T           (fitness function uses T trials, default 5)"
        print "   -s S           (sim seconds per trial, default 20)"
        print "   -z Z           (population size, default 100)"
        print "   -m M           (max generations, default 100)"
        print "   -c 0|1         (can hear?, default 1)"
        print
        print " CONTROL+c to stop at next end of generation"
        print " CONTROL+c CONTROL+c to stop now"
        sys.exit()
    if sys.argv[i] == "-g":
        i += 1
        simType = sys.argv[i].lower()
        if simType == "2d":
            SimulatorClass, PioneerClass = TkSimulator, TkPioneer
        elif simType == "none":
            SimulatorClass, PioneerClass = Simulator, Pioneer
        elif simType == "3d":
            from pyrobot.simulators.pysim3d import Tk3DSimulator
            SimulatorClass, PioneerClass = Tk3DSimulator, TkPioneer
        else:
            raise AttributeError("unknown graphics mode: '%s'" % simType)
    elif sys.argv[i] == "-n":
        i += 1
        robotCount = int(sys.argv[i])
    elif sys.argv[i] == "-a":
        automaticRestart = True
    elif sys.argv[i] == "-l":
        i += 1 
        loadPop = sys.argv[i]
    elif sys.argv[i] == "-t":
        i += 1 
        numTrials = int(sys.argv[i])
    elif sys.argv[i] == "-s":
        i += 1 
        numSeconds = int(sys.argv[i])
    elif sys.argv[i] == "-z":
        i += 1 
        numPopsize = int(sys.argv[i])
    elif sys.argv[i] == "-m":
        i += 1 
        numMaxgen = int(sys.argv[i])
    elif sys.argv[i] == "-c":
        i += 1 
        canHear = int(sys.argv[i])
    elif sys.argv[i] == "-e":
        startEvolving = True
    elif sys.argv[i] == "-p":
        i += 1 
        if sys.argv[i].lower() == "none":
            sd = None
        else:
            sd = sys.argv[i]
    i += 1

try:
    sd = SoundDevice(sd)
except:
    sd = None
    print "Sound device failed to start"

############################################################
# Build a simulated world:
############################################################
# In pixels, (width, height), (offset x, offset y), scale:
sim = SimulatorClass((441,434), (22,420), 40.357554, run=0)  
## Milliseconds of time to simulate per step:
sim.timeslice = 250
# Add a bounding box:
# x1, y1, x2, y2 in meters:
sim.addBox(0, 0, 10, 10)
# Add a couple of light sources:
# (x, y) meters, brightness usually 1 (1 meter radius):
sim.addLight(2, 2, 1)
sim.addLight(7, 7, 1)

for i in range(robotCount):
    # port, name, x, y, th, bounding Xs, bounding Ys, color
    sim.addRobot(60000 + i, PioneerClass("Pioneer%d" % i,
                                         1, 1, -0.86,
                                         ((.225, .225, -.225, -.225),
                                          (.15, -.15, -.15, .15)),
                                         colors[i]))
    robot = sim.robots[-1] # last one
    robot.addDevice(PioneerFrontSonars())
    robot.addDevice(PioneerFrontLightSensors())

############################################################
# Now, make some connections to the sim robots
############################################################

# client side:
clients = [Simbot(sim, ["localhost", 60000 + n], n) for n in range(robotCount)]
# server side:
engines = [Engine() for n in range(robotCount)]
for n in range(robotCount):
    engines[n].robot = clients[n]
    # turn off noise:
    clients[n].light[0].noise = 0.0
    clients[n].sonar[0].noise = 0.0
    # load brain:
    engines[n].brain = NNBrain(engine=engines[n])

# Set some properties after robots are created:
for n in range(robotCount):
    sim.display["%s robot audio" % colors[n]] = False
if isinstance(sim, TkSimulator):
    sim.toggle("trail")
    sim.toggle("speech")
    sim.toggle("sonar")
    alist = []
    for n in range(robotCount):
        s = "%s robot audio" % colors[n]
        alist.append([s, lambda s=s: sim.simToggle(s)])
    menu = [('Program', alist)]
    for entry in menu:
        sim.mBar.tk_menuBar(sim.makeMenu(sim.mBar, entry[0], entry[1]))
sim.redraw()

############################################################
# Define some functions for hearing support
############################################################

def quadNum(myangle, angle):
    """
    Given angle, return quad number
      |0|
    |3| |1|
      |2|
    """
    diff = angle - myangle
    if diff >= 0:
        if diff < math.pi/4:
            return 0
        elif diff < math.pi/4 + math.pi/2:
            return 3
        elif diff < math.pi:
            return 2
        else:
            return 1
    else:
        if diff > -math.pi/4:
            return 0
        elif diff > -math.pi/4 - math.pi/2:
            return 1
        elif diff > -math.pi:
            return 2
        else:
            return 3

def quadTest(robot = 0):
    location = [0] * robotCount
    for n in range(robotCount):
        location[n] = engines[0].robot.simulation[0].getPose(n)
    myLoc = location[robot]
    return quadSound(myLoc, range(robotCount), location)

def quadSound(myLoc, lastS, location):
    """
    Computes the sound heard for all quads.
    myLoc:    (x, y, t) of current robot; t where 0 is up
    lastS:    last sound made by robots
    location: (x, y, t) of robots; t where 0 is up
    """
    if not canHear:
        return [0.5 for x in range(robotCount)]
    # dist, freq for each robot; 0.5 is what is silence
    closest = [(10000,0.5), (10000,0.5), (10000,0.5), (10000,0.5)] 
    for n in range(len(location)):
        loc = location[n]
        if loc != myLoc:
            # distance between robots:
            dist = distance(myLoc[0], myLoc[1], loc[0], loc[1])
            # global angle from one robot to another:
            # 0 to right, neg down (geometry-style)
            angle = Polar(loc[0] - myLoc[0], loc[1] - myLoc[1], bIsPolar=0) 
            angle = angle.t # get theta
            if angle < 0:
                angle = math.pi + (math.pi + angle) # 0 to 2pi
            angle = (angle - math.pi/2) % (math.pi * 2)
            q = quadNum(myLoc[2], angle) 
            #print n, myLoc[2], angle, q
            # if shorter than previous, and less than N meters
            if dist < closest[q][0] and dist < 1.0/2.7 * 7.0: 
                closest[q] = dist, lastS[n] # new closest
    return [v[1] for v in closest] # return the sounds

############################################################
# Now, let's define the GA:
############################################################

class NNGA(GA):

    def __init__(self, *args, **kwargs):
        self.pre_init = 1
        GA.__init__(self, *args, **kwargs)
        self.pre_init = 0
        self.done = 0
        self.randomizePositions()

    def generate(self):
        if self.generation == 1: return
        elitePositions = map(lambda x: x.position, self.pop.eliteMembers)
        elitePositions.sort()
        # Move all good ones to front of the line:
        for i in range(len(self.pop.eliteMembers)):
            #print "   move", elitePositions[i], "to", i
            self.pop.individuals[i] = self.pop.individuals[elitePositions[i]]
        # Populate the rest of the pop with copies of these:
        for i in range(len(self.pop.eliteMembers)):
            copies = ((self.pop.size - len(self.pop.eliteMembers))/
                      len(self.pop.eliteMembers))
            for j in range(copies):
                pos = (i * copies) + len(self.pop.eliteMembers) + j
                #print "   copy", i, "to", pos
                self.pop.individuals[pos] = self.pop.individuals[i].copy()
                self.pop.individuals[pos].mutate(self.mutationRate)

    def loadWeights(self, genePos):
        for n in range(len(engines)):
            engine = engines[n]
            engine.brain.net.unArrayify(self.pop.individuals[genePos].genotype)

    def randomizePositions(self, seed=None):
        # seed = 0 (reinit), seed = None (random), seed = num (seed it)
        if seed == 0: # Reinitialize to something random:
            seed = random.random() * 100000 + time.time()
        if seed != None: # use a specific seed:
            random.seed(seed)
        # Make the robots far from these positions:
        positions = [(2, 2), (7, 7)] # position of lights
        for n in range(len(engines)):
            engine = engines[n]
            # Put each robot in a random location:
            x, y, t = (1 + random.random() * 7, 
                       1 + random.random() * 7, 
                       random.random() * math.pi * 2)
            minDistance = min([distance(x, y, x2, y2) for (x2,y2) in positions])
            # make sure they are far enough apart:
            while minDistance < 2: # in meters
                x, y, t = (1 + random.random() * 7, 
                           1 + random.random() * 7, 
                           random.random() * math.pi * 2)
                minDistance = min([distance(x, y, x2, y2) 
                                   for (x2,y2) in positions])
            positions.append( (x,y) )
            engine.robot.simulation[0].setPose(n, x, y, t)
        sim.redraw()

    def fitnessFunction(self, genePos, randomizeSeed=None):
        # seed = -1 (cont), seed = 0 (reinit), seed = None (random), 
        # seed = num (seed it)
        if self.pre_init: # initial generation fitness
            return 1.0
        fitness = 0.01
	print "-------------------------------"
        for count in range(numTrials):
            subfitness = 0.01
            if genePos >= 0: # -1 is test of last one
                self.loadWeights(genePos)
            if randomizeSeed == -1:
                pass # continue
            else:
                # seed = 0 (reinit), seed = None (random), seed = num (seed it)
                self.randomizePositions(randomizeSeed)
            sim.resetPaths()
            sim.redraw()
            s = [0] * robotCount # each robot's sound
            lastS = [0] * robotCount # previous sound
            location = [(0, 0, 0) for v in range(robotCount)] 
            # Set the context values to zero:
            for n in range(robotCount): # number of robots
                engine = engines[n]
                engine.brain.net.setContext(0.5)
                engine.brain.net["output"].setActivations(0.5)
                engine.brain.net["output"].resetActivationFlag()
            for i in range(self.seconds * (1000/sim.timeslice)): # (10 per sec)
                # ------------------------------------------------
                # First, get the locations:
                # ------------------------------------------------
                for n in range(robotCount): # number of robots
                    location[n] = engines[0].robot.simulation[0].getPose(n)
                # ------------------------------------------------
                # Next, compute the move for each robot
                # ------------------------------------------------
                for n in range(robotCount): # number of robots
                    engine = engines[n]
                    engine.robot.update()
                    # compute quad for this robot
                    myLoc = location[n]
                    quad = quadSound(myLoc, lastS, location)
                    # print n, quad
                    # compute output for each robot
                    oTrans, oRotate, s[n] = engine.brain.propagate(quad)
                    # then set the move velocities:
                    engine.brain.step(oTrans, oRotate)
                    sim.robots[n].say("%.2f Heard: [%s]" % 
                                      (s[n], 
                                       ",".join(map(lambda v: "%.2f" % v, quad))))
                # ------------------------------------------------
                # Save the sounds
                # ------------------------------------------------
                for n in range(robotCount): # number of robots
                    lastS = [v for v in s]
                # ------------------------------------------------
                # Make the move:
                # ------------------------------------------------
                sim.step(run=0)
                # update tasks in GUI:
                if isinstance(sim, TkSimulator):
                    while sim.tk.dooneevent(2): pass
                # Stop the robots from moving on other steps:
                for n in range(robotCount): # number of robots
                    engine = engines[n]
                    engine.robot.stop()
                # play a sound, need to have a sound thread running
                for n in range(robotCount): # number of robots
                    st = "%s robot audio" % colors[n]
                    if sim.display[st] and sd != None:
                        sd.playTone(int(round(engines[n].brain.net["output"].activation[-1], 1) * 2000) + 500, .1) # 500 - 2500
                # ------------------------------------------------
                # Compute fitness
                # ------------------------------------------------
                closeTo = [0, 0] # number of lights
                # how many robots are close to which lights?
                for n in range(len(engines)):
                    engine = engines[n]
                    # get global coords
                    x, y, t = engine.robot.simulation[0].getPose(n)
                    # which light?
                    dists = [distance(light.x, light.y, x, y) 
                             for light in sim.lights]
                    if min(dists) <= 1.0:
                        if dists[0] < dists[1]:
                            closeTo[0] += 1
                        else:
                            closeTo[1] += 1
                # ------------------------------------------------
                # Finally, compute the fitness
                # ------------------------------------------------
                for total in closeTo:
                    subfitness += .25 * total
                    # only allow N per feeding area
                    if total > 2:
                        subfitness -= 1.0 * (total - 2)
                    subfitness = max(0.01, subfitness)
                #print "   ", closeTo, subfitness,
                #raw_input(" press [ENTER]")
            print "   subfitness: %d: %.5f" % (genePos,subfitness)
            fitness += subfitness
        print "Total Fitness %d: %.5f" % (genePos, fitness)
        return fitness
    def setup(self, **args):
        if args.has_key('seconds'):
            self.seconds = args['seconds']
        else:
            # default value
            self.seconds = 20 # how much simulated seconds to run
    def isDone(self):
        if self.generation % 1 == 0:
            self.saveGenesToFile("gen-%05d.pop" % self.generation)
            # load the best into a network:
            engines[0].brain.net.unArrayify(self.pop.bestMember.genotype)
            # and save it
            engines[0].brain.net.saveWeightsToFile("best-%05d.wts" % 
                                                   self.generation)
        return self.done

class Experiment:
    def __init__(self, seconds, popsize, maxgen):
        g = engines[0].brain.net.arrayify()
        self.ga = NNGA(Population(popsize, Gene, size=len(g), verbose=1,
                                  imin=-1, imax=1, min=-50, max=50, maxStep = 1,
                                  elitePercent = .20),
                       mutationRate=0.02, crossoverRate=0.6,
                       maxGeneration=maxgen, verbose=1, seconds=seconds)
    def evolve(self, cont=0):
        self.ga.done = 0
        self.ga.evolve(cont)
    def stop(self):
        for n in range(robotCount):
            engines[n].robot.stop()
    def saveBest(self, filename):
        net = engines[0].brain.net
        net.unArrayify(self.ga.pop.bestMember.genotype)
        net.saveWeightsToFile(filename)
    def loadGenotypes(self, filename):
        engines[0].brain.net.loadWeightsFromFile(filename)
        genotype = engines[0].brain.net.arrayify()
        for p in self.ga.pop:
            for n in range(len(genotype)):
                p.genotype[n] = genotype[n]
    def loadWeights(self, filename):
        for n in range(robotCount):
            engines[n].brain.net.loadWeightsFromFile(filename)
    def test(self, seconds):
        self.ga.seconds = seconds
        return self.ga.fitnessFunction(-1) # -1 testing

def testSpeed(steps=100):
    start = time.time()
    for i in range(steps):
        for client in clients:
            client.update()
        for engine in engines:
            engine.brain.step(1,1)
        sim.step(run=0)
        if isinstance(sim, TkSimulator):
            while sim.tk.dooneevent(2): pass
    stop = time.time()
    print "Average steps per second:", float(steps)/ (stop - start)
    print "%.2f x realtime" % (((float(steps)/ (stop - start)) / 10.0))

# ------------------------------------------------
# Hack to shutdown engine threads, but keep robot:
# ------------------------------------------------
for e in engines:
    temp = e.robot
    e.pleaseStop()
    e.shutdown()
    e.robot = temp

# ---------------------------------------------------------------------
# Code to handle control+c: once to exit at end of generation; twice to 
# abort right now.
# ---------------------------------------------------------------------
def suspend(*args):
    if not e.ga.done: # first time
        print "# ------------------------------------------"
        print "# Setting GA to stop at end of generation..."
        print "# ------------------------------------------"
        e.ga.done = 1
    else:
        print "# ------------------------------------------"
        print "# Stopping..."
        print "# ------------------------------------------"
        raise KeyboardInterrupt
import signal
signal.signal(signal.SIGINT,suspend)

e = Experiment(seconds=numSeconds, popsize=numPopsize, maxgen=numMaxgen)
if automaticRestart:
    import glob
    maxI = None
    flist = glob.glob("./gen-*.pop")
    if len(flist) > 0:
        flist.sort()
        filename = flist[-1]
        e.ga.loadGenesFromFile(filename)
        e.ga.generation = int(filename[6:11])
elif loadPop:
    e.ga.loadGenesFromFile(loadPop)
if startEvolving:
    e.evolve(cont=1)

# Other commands to try:
#e.ga.randomizePositions() # pick random places
#e.ga.randomizePositions(7652361) # seed to use
#e.ga.fitnessFunction(23, randomize=0) # test #23, do not reposition
#e.ga.fitnessFunction(-1) # test again in random place
#e.ga.fitnessFunction(-1, randomize=0) # test again in this place
#e.evolve(cont=1) # continues from before
#e.loadWeights("nolfi-100.wts")
#e.loadGenotypes("nolfi-100.wts")
#e.evolve()
#e.saveBest("nolfi-200.wts")
#e.ga.saveGenesToFile("nolfi-20-20-100.pop")

