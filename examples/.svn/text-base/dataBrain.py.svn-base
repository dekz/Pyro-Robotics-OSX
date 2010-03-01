# vim:sw=4:expandtab:sts=4:
"""


A Subsumption Behavior-Based Brain with Wall- and Freespace- Following
----------------------------------------------------------------------
G. Dahl and A. Pshenichkin - gdahl1, apsheni1@swarthmore.edu
Created Novermber 3, 2005.

Based on 'SubsumptionFindLight.py', a simple brain by Lisa Meeden


This is a Subsumption-based brain, designed to quickly and efficiently 
navigate most worlds looking for a light source, and then to change methods if 
it can't find anything using its original technique.

Specifically, it has the following layers:
Layer 0: Wander - the default wonder method, left in to catch any situations 
        in which no other rules fire
Layer 1: WhitespaceFollow - a freespace-following behavior; very active from 
        the beginning and the most important and effective of our strategies
Layer 2: TimedWallFollow - a wall-following behavior that only activates 
        sporadically, based on a timer, used to reach areas that freespace-
        following alone would miss
Layer 3: SeekLight - a simple drive-towards-the-light behavior for the last 
        leg of the robot's journey
Layer 4: Avoid - the robot tries its best not to hit walls
Layer 5: StallRecover - a quick and dirty stall recovery method
Layer 6: FoundLight - the robot stops when it finds the light

Essentially, the robot uses a freespace-following algorithm to find its way 
around the world, and then switches to a wall-follower if freespace-following 
doesn't reach the goal in a reasonable amount of time (some things, such as 
time spent trying to get out of a corner, don't actually count against it). If, 
subsequently, wall-following also doesn't find the goal, we switch back to 
freespace-following for a while and the cycle continues; more time is set aside 
for wall-following with each loop (the logic being that finding a tiny crevice 
is going to be more time-consuming than simply moving around looking for big 
patches of empty space).

This robot can successfully navigate all of the default worlds, as well as more 
difficult worlds such as the "Light in Maze" world with discontinuous walls. It 
exhibits near-optimal behavior in most cases, though the speed could perhaps be 
tuned to improve performance in some scenarios (we try not to be *too* fast).
"""

from pyrobot.brain import Brain
import time
import random

class SubsumptionBehavior:
    # This is Lisa's SubsumptionBehavior base class, with slight modification.
    def __init__(self):
        self.translate = 0
        self.rotate = 0
        self.flag = 0

        # added speed constants here for easier tuning
        # (most rotations should be proportional to the speed, then)
        self.spd_slow = 0.1
        self.spd_med = 0.4
        self.spd_fast = 0.6

    def setRobot(self, robot):
        self.robot = robot

    def move(self, translate, rotate):
        self.translate = translate
        self.rotate = rotate
        self.flag = 1

class SubsumptionBrain(Brain):
    # This is Lisa's SubsumptionBrain class, unmodified.
    def __init__(self, engine):
        Brain.__init__(self, 'SubsumptionBrain', engine)
        self.behaviors = []
        self.robot = engine.robot
        self.robot.light[0].units = "SCALED"
        self.inputFile = open("inputs.dat", "w")
        self.targetFile = open("targets.dat", "w")

    def add(self, behavior):
        behavior.setRobot( self.robot )
        self.behaviors.append( behavior )

    def step(self):
        b = self.updateAll()
        print ("%s is in control b " % (self.behaviors[b].__class__.__name__))
        self.move(self.behaviors[b].translate,\
                  self.behaviors[b].rotate)
        if b < 6:
             for i in range(8):
                 self.inputFile.write("%f " % self.robot.range[i-1].distance(unit = "SCALED"))
             self.inputFile.write("%f %f" % (self.robot.light[0][0].value, self.robot.light[0][1].value))
             self.inputFile.write(" %f\n" % self.robot.stall)
             self.targetFile.write("%f %f\n" % ( (self.behaviors[b].translate +1)/2, (self.behaviors[b].rotate +1)/2))
             self.targetFile.flush()
             self.inputFile.flush()
        time.sleep(1)

    def updateAll(self):
        # for all except lowest:
        for b in range(len(self.behaviors) - 1, 0, -1):
            self.behaviors[b].flag = 0
            self.behaviors[b].update()
            # if it fired, return number:
            if self.behaviors[b].flag:
                return b
        # if none fired, return lowest:
        self.behaviors[0].update()
        return 0

# -----------------------------------------------------

class Wander(SubsumptionBehavior):
    """
    This is a basic Wander function, unchanged from the original. Note that 
    our architecture never results in this being called, but it is left in here 
    so that there is always a default method for dealing with stuff.
    """
    def update(self):
        self.move( .3, random.random() - 0.5)

class WhitespaceFollow(SubsumptionBehavior):
    """
    This is a freespace following behavior. By looking at each sensor 
    individually and weighing them more-or-less based on their angles, we can 
    generate very nice, smooth motion. This is the work horse of our 
    implementation, and tends to find the goal quickly and efficiently on most 
    worlds.
    """
    def update(self):
        # rank sensors based on location from the middle
        # assuming a Pioneer, we have:
        #        2  3
        #     1        4
        #  0              5

        # find max of (front-left, front-right, front)
        list = [s.value for s in self.robot.range["front-all"]]
        for i in list:
            if i > 1.6: # limit values
                i = 1.6
        max_idx = list.index(max(list))
        # on the scheme above, 2.5 would be "straight ahead", so...
        rot = -(max_idx-2.5)*(self.spd_fast/3.0) # hopefully speed-safe
        self.move(self.spd_fast, rot)

class SeekLight(SubsumptionBehavior):
    """
    This is the basic SeekLight behavior, which simply causes a robot to try to 
    move towards any light that it sees, modified slightly to use our speed 
    settings.
    """
    def update(self):
        if  max([s.value for s in self.robot.light[0]["all"]]) > 0.0:
            left = max([s.value for s in self.robot.light[0]["left"]])
            right = max([s.value for s in self.robot.light[0]["right"]])
            rotation = left - right
            rotation = rotation*(self.spd_med/0.1)
            if left > right:
                self.move(self.spd_med, rotation + self.spd_med/1.5)
            else:
                self.move(self.spd_med, rotation - self.spd_med/1.5)

class FoundLight(SubsumptionBehavior):
    """
    When we find a light, we stop.
    """
    def update(self):
        if max([s.value for s in self.robot.light[0]["all"]]) > 0.9:
            self.move(0.0, 0.0)

class Avoid(SubsumptionBehavior):
    """
    This is the basic Avoid function, slightly refactored but left very much 
    intact.
    """
    def __init__(self):
        # we added this treshold constant
        self.avoid_threshold = 1.0
        SubsumptionBehavior.__init__(self)
    def update(self):
        if min([s.value for s in self.robot.range["front-all"]]) < \
                self.avoid_threshold:
            frontLeft= min([s.value for s in self.robot.range["front-left"]])
            frontRight= min([s.value for s in self.robot.range["front-right"]])
            if frontLeft < frontRight:
                self.move(self.spd_slow, -1.0 + frontLeft)
            else:
                self.move(self.spd_slow, 1.0 - frontRight)

class TimedWallFollow(SubsumptionBehavior):
    """
    This subsumption behavior integrates a wall-follower into our robot. 
    Because our freespace-follower works so well and the two can't really run 
    together, TimedWallFollow only exists to catch situations that fall through 
    the cracks. We do this by having a counter (self.numSteps) that gets 
    incremented every time this behavior is invoked. If the counter is too low, 
    we simply pass control onto the function below us, just like any other 
    behavior that doesn't trigger. If it is sufficiently high, we wall-follow 
    instead, using an approximation of the typical "equalize two side sensors"
    algorithm. The wall-follower has a favored side, which changes with time. 
    Generally, the robot will intermix periods of wall- and freespace-
    following, which should allow it to find its way through almost any map in 
    a fairly reasonable amount of time. Time spent in higher-level layers like 
    Avoid, which tends to be highly variable, is not counted.
    """
    def __init__(self):
        self.numSteps = 0
        self.onsetDelay = 90 # don't set below ~75!
        self.wallFollowTimer = 70
        self.left_handed = True # default to left-handed wall-following
        SubsumptionBehavior.__init__(self)
    def update(self):
        self.numSteps += 1
        print "counter:", self.numSteps
        allSonar = [s.value for s in self.robot.range["front-all"]] # the front
        self.left = [s.value for s in self.robot.range["left"]][0] # the sides
        self.right = [s.value for s in self.robot.range["right"]][0]
        if self.numSteps == self.onsetDelay:
            print "Switching to wall-following"
        if self.numSteps > self.onsetDelay:
            # if our other layers have not found the goal, try enabling wall
            # following
            forward = 0
            rot = 0
            if self.left_handed:
                # left wall following
                if self.left < allSonar[0]*0.8:
                    # we want to approximate the effect of two parallel light 
                    # sensors on each side of the robot; to do this, we pick 
                    # the side sensor and the front-side sensor closest to it, 
                    # note that the angle between them is ~25 degrees, then do 
                    # some basic trig and rounding to get the above relation, 
                    # which indicates that we want to turn toward the wall some 
                    # more - this is a good way to find "doors" when we run 
                    # across them, too
                    
                    # turn left
                    rot = 0.5
                    forward = self.spd_med
                else:
                    # move forward
                    forward = self.spd_med
            else:
                # right wall following
                if self.right < allSonar[5]*0.8:
                    # this is symmetrical to the left case; see above
                    
                    # turn right
                    rot = -0.5
                    forward = self.spd_meed
                else:
                    # move forward
                    forward = self.spd_med
            self.move(forward, rot)
        if self.numSteps > self.onsetDelay + self.wallFollowTimer:
            # every time we fail to freespace-follow our way to glory in a set 
            # time, we try the clunkier wallspace-follower, which sticks to a
            # wall on one side of the robot for self.wallFollowTimer iterations 
            # before giving control up to the freespace-follower again
            
            self.left_handed = not self.left_handed # change handedness

            # tweak our parameters for less freespace-following and more wall-
            # following on the next run-through of the counter
            self.wallFollowTimer = self.wallFollowTimer + 20
            self.onsetDelay = self.onsetDelay - 10
            if self.onsetDelay < 20:
                self.onsetDelay = 20
            self.numSteps = 0
            print "Switching to free-space following"

class StallRecover(SubsumptionBehavior):
    """
    This is a very simple method for stall recovery: the robot simply tries to 
    move backwards and turn randomly.
    """
    def update(self):
        if self.robot.stall:
            if min([s.value for s in self.robot.range["front"]]) < 0.25:
                # we're stuck in front
                self.move(-self.spd_med, random.random() - 0.5)
            else:
                # we're stuck somewhere in back... try just going forward
                self.move(self.spd_slow, 0.0)

def INIT(engine):
    subsumption = SubsumptionBrain( engine )
    # add behaviors, lowest priorities first:
    subsumption.add( Wander() )
    subsumption.add( WhitespaceFollow() )
    subsumption.add( TimedWallFollow() )
    subsumption.add( SeekLight() )
    subsumption.add( Avoid() )
    subsumption.add( StallRecover() )
    subsumption.add( FoundLight() )
    return subsumption
