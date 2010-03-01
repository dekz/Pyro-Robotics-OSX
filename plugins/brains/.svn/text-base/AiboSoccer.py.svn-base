"""
Author: Ioana Butoi
Date: Apr 2005

Project: Two robots play soccer against each other
         Each of them controls half of the arena. Each half of the court is
         colored differenly. 
Robot: Aibo ERS-7
"""

from pyrobot.brain.behaviors.fsm import *
from time import sleep
import random

matchBall = 25
matchGoal = 40
        
class RobotVsRobotSoccer(FSMBrain):
    def setup(self):
        camera = self.robot.camera[0]
        # goal filter
        camera.addFilter("match", 64, 104, 153, 30, 2)#blue
        camera.addFilter("blobify",2,255,255,0,1,1,1,)#blue
        
        # ball filter
        #camera.addFilter("matchRange",178,19,41,250,101,214,0)#pink ball
        camera.addFilter("match", 193, 27, 31,70)#red ball
        camera.addFilter("blobify",0,255,255,0,1,1,1,)
      

    def destroy(self):
        self.camera[0].clearFilters()

class approachBall(State):
    """
    When a ball is in sight, get close to it
    """
    def onActivate(self):
        self.speed = 0.05
        self.turnSpeed = 0.1
        self.headMaxTurn = 0.3
        print "APPROACH"

    def step(self):
        results = self.robot.camera[0].filterResults
        if len(results) > 1 and len(results[-1]) > 0: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a blob in sight
                x1, y1, x2, y2, area = results[-1][0]
                centerX, centerY = (x1 + x2)/2, (y1 + y2)/2
                if area > matchBall:
                    pose = self.robot.ptz[0].pose # p,t,z,r; acts as a pointer
                    # 1. center camera on ball
                    # ---------------X direction------------------
                    diff = (centerX - (self.robot.camera.width/2))
                    if abs(diff) < (.1 * self.robot.camera.width):
                        pass
                    elif diff < 0:
                        # negative is right, positive is left
                        self.robot.ptz[0].pan( pose[0] + self.speed) 
                    else:
                        self.robot.ptz[0].pan( pose[0] - self.speed) 
                    # ---------------Y direction------------------
                    diff = (centerY - self.robot.camera.height/2) 
                    if abs(diff) < .1 * self.robot.camera.height:
                        pass
                    elif diff < 0: # down
                        self.robot.ptz[0].tilt( pose[1] + self.speed) # positive is left
                    else:
                        self.robot.ptz[0].tilt( pose[1] - self.speed) # negative is right
                    # 2. get closer to ball
                    if abs(pose[0]) > self.headMaxTurn:
                        # 2.1 rotate so ball is in front of you
                        if pose[0] > 0:
                            self.robot.move(0,self.turnSpeed)
                            self.robot.ptz[0].pan(pose[0] - self.speed)
                        else:
                            self.robot.move(0,-self.turnSpeed)
                            self.robot.ptz[0].pan(pose[0] + self.speed)
                    elif area<300:
                        # 2.2 get closer to ball
                        self.robot.move(0.7,0)
                    else:
                        # 3. when close enough kick it
                        self.goto("lookForGoal")
                        return
                else:
                    self.goto("lostBall", centerX, centerY)
                    return
            else:
                self.goto("searchDown")
                return
        else:
            self.goto("searchDown")
            return
        

class lostBall(State):
    """
    Ball moved out of my sight. I think I know where it went
    """
    def onActivate(self):
        self.robot.move(0,0)
        self.speed = 0.1
        print "LOST"

    def onGoto(self, args):
        self.ballCenterX = args[0]
        self.ballCenterY = args[1]
        
    def step(self):
        results = self.robot.camera[0].filterResults
        if len(results) > 1 and len(results[-1]) > 0: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a blob in sight
                x1, y1, x2, y2, area = results[-1][0]
                if area > matchBall:
                    self.goto("approachBall")
                    return
        pose = self.robot.ptz[0].pose# p,t,z,r; acts as a pointer
        diffX = abs(self.ballCenterX - self.robot.camera.width/2)
        diffY = abs(self.ballCenterY - self.robot.camera.height/2)
        if diffX > diffY:
            turnDirVer = 0
            # need to search horizontally
            if (self.ballCenterX > self.robot.camera.width/2):
                # right
                turnDirHor = -1
            else:
                # left
                turnDirHor = 1
        else:
            turnDirHor = 0
            if (self.ballCenterY > self.robot.camera.width/2):
                # down
                turnDirVer = -1
            else:
                turnDirVer = 1
        self.robot.ptz[0].pan(pose[0]+ turnDirHor*self.speed)
        self.robot.ptz[0].tilt(pose[1] + turnDirVer*self.speed)
        if (((pose[0] == 1.0 or pose[0] == -1.0) and turnDirVer == 0) or
            ((pose[1] == -1.0 or pose[1] == 0.0) and turnDirHor == 0)):
            self.goto("searchDown")

class searchDown(State):
    """
    Searches for the ball by turning the head down
    """
    def onActivate(self):
        self.robot.ptz[0].center()
        self.speed = 0.1
        print "DOWN"
        
    def step(self):
        pose = self.robot.ptz[0].pose
        results = self.robot.camera[0].filterResults
        if len(results) > 1 and len(results[-1]) > 0: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a blob in sight
                x1, y1, x2, y2, area = results[-1][0]
                if area > matchBall:
                    self.goto("approachBall")
                    return
        self.robot.ptz[0].tilt(pose[1] - self.speed)
        if (pose[1] < -0.9):
            self.goto("searchLeftRight")

class searchLeftRight(State):
    """
    Searches for the ball by turning the head left-right
    """
    def onActivate(self):
        self.robot.ptz[0].tilt(-0.1)
        sleep(1)
        self.robot.ptz[0].pan(1.0)
        self.speed = 0.05
        print "L - R"


    def step(self):
        pose = self.robot.ptz[0].pose
        results = self.robot.camera[0].filterResults
        if len(results) > 1 and len(results[-1]) > 0: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a blob in sight
                x1, y1, x2, y2, area = results[-1][0]
                if area > matchBall:
                    self.goto("approachBall")
                    return
        self.robot.ptz[0].pan(pose[0] - self.speed)
        if (pose[0] == -1.0):
            self.goto("searchRightLeft")



class searchRightLeft(State):
    """
    Searches for the ball by turning the head right-left
    """
    def onActivate(self):
        self.robot.ptz[0].tilt(-0.6)
        sleep(0.5)
        self.robot.ptz[0].pan(-1.0)
        self.speed = 0.05
        print "R - L"

    def step(self):
        pose = self.robot.ptz[0].pose
        results = self.robot.camera[0].filterResults
        if len(results) > 1 and len(results[-1]) > 0: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a blob in sight
                x1, y1, x2, y2, area = results[-1][0]
                if area > matchBall:
                    self.goto("approachBall")
                    return
        self.robot.ptz[0].pan(pose[0] + self.speed)
        if (pose[0] == 1.0):
            self.goto("searchDynamic")

                 

        
class searchDynamic(State):
    """
    Searches for the ball by spinning in place
    """
    def onActivate(self):
        self.robot.ptz[0].center()
        self.robot.ptz[0].tilt(-0.1)
        self.counter = 0
        if random.random() > 0.5: # randomize the turn direction
            self.turnSpeed = 0.2
        else:
            self.turnSpeed = -0.2
            
    def step(self):
        results = self.robot.camera[0].filterResults
        if len(results) > 1 and len(results[-1]) > 0: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a blob in sight
                x1, y1, x2, y2, area = results[-1][0]
                if area > matchBall:
                    self.goto("approachBall")
                    return
        self.counter +=1
        if self.counter == 50:# after 360 change the angle
            self.robot.ptz[0].tilt(-0.5)
        self.robot.move(0.0,self.turnSpeed)

class prepareToKick(State):
    def onActivate(self):
        self.robot.move(0,0)
        self.robot.playSound("mew")
        self.speed = 0.05
        self.turnSpeed= 0.1
        self.turnHeadMin = 0.4
        self.turnHeadMax = 0.5
        print "PREPARE TO KICK"

    def step(self):
        results = self.robot.camera[0].filterResults
        if len(results) > 1 and len(results[-1]) > 0: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a blob in sight
                x1, y1, x2, y2, area = results[-1][0]
                if area> 50:
                    # 1.center the image
                    centerX, centerY = (x1 + x2)/2, (y1 + y2)/2
                    pose = self.robot.ptz[0].pose # p,t,z,r
                    # ---------------X direction------------------
                    diff = (centerX - (self.robot.camera.width/2))
                    if abs(diff) < (.1 * self.robot.camera.width):
                        pass
                    elif diff < 0:
                        # negative is right, positive is left
                        self.robot.ptz[0].pan( pose[0] + self.speed) 
                    else:
                        self.robot.ptz[0].pan( pose[0] - self.speed) 
                    # ---------------Y direction------------------
                    diff = (centerY - self.robot.camera.height/2) 
                    if abs(diff) < .1 * self.robot.camera.height:
                        pass
                    elif diff < 0: # down
                        self.robot.ptz[0].tilt( pose[1] + self.speed) # positive is left
                    else:
                        self.robot.ptz[0].tilt( pose[1] - self.speed) # negative is right
                    # 2. put your foor next to the ball
                    if  abs(pose[0]) >= self.turnHeadMin and abs(pose[0]) <= self.turnHeadMax:
                        # 3.move close enough
                        if (x2-x1 + y2-y1 < 140):

                            self.robot.move(0.1,0.0)
                        else:
                            self.goto("kick")
                            return
                    elif abs(pose[0]) < self.turnHeadMin:
                        if pose[0] < 0:
                            self.robot.move(0,self.turnSpeed)
                        else:
                            self.robot.move(0,-self.turnSpeed)
                    elif abs(pose[0]) > self.turnHeadMax:
                        if pose[0] < 0:
                            self.robot.move(0,-self.turnSpeed)
                        else:
                            self.robot.move(0,self.turnSpeed)
                else:
                    self.goto("approachBall")
        else:
            self.goto("searchDown")

class kick(State):
    def onActivate(self):
        self.robot.move(0,0)
        self.pose = self.robot.ptz[0].pose # p,t,z,r
        if (self.pose[0] > 0):
            self.leg = "left"
        else:
            self.leg = "right"
        self.robot.ptz[0].center()
        print "KICK"

    def step(self):

        # 1. stand on 3 legs:
        #   move the weight on the oposite side of kicking
        self.robot.setPose(self.leg+" back leg",-0.3,0.2,0.8) 
        sleep(1)
        self.robot.setPose(self.leg+" back leg",-0.5,0.15,0.7)
        sleep(1)
        # 2. kick
        self.robot.setPose(self.leg+ " front leg",0.7, 0.1, 0.3)
        sleep(1.0)
        # 3. bring leg to initial position
        self.robot.setPose(self.leg+" front leg rotator",0.0)
        sleep(1.0)
        # 4. distribute weight on all 4 legs
        self.robot.setPose(self.leg+" back leg ", -0.3,0.1,0.8)
        self.robot.move(0.1,0)
        self.goto("didYouScore")

class lookForGoal(State):
    def onActivate(self):
        self.robot.move(0,0)
        self.p,self.t, self.z,self.r = self.robot.ptz[0].pose # remember where you were looking
        self.robot.ptz[0].center()
        if random.random() > 0.5:
            self.maxTurn = -1.0
            self.speed = 0.1
        else:
            self.maxTurn = 1.0
            self.speed = -0.1
        self.robot.ptz[0].pan(self.maxTurn)
        sleep(1)
        print "LOOK FOR GOAL"

    def step(self):
        results = self.robot.camera[0].filterResults
        pose = self.robot.ptz[0].pose
        if len(results) > 1 and len(results[1]) > 0: # need a match, and blobify at least
            if len(results[1][0]) == 5: # have a goal blob in sight
                x1, y1, x2, y2, area = results[1][0]
                if area >35:
                    sleep(1)
                    if abs(pose[0]) > 0.1:
                        if pose[0] > 0:
                            dir = -1 # left
                        else:
                            dir = 1
                    else:
                        self.goto("findGoal",[self.p,self.t,self.z,self.r],0)
                        return
                    self.goto("findGoal", [self.p,self.t,self.z,self.r], dir)
                    return
        if (pose[0] == -self.maxTurn):
            if random.random()>0.5:# randomize direction
                dir = 1
            else:
                dir = -1
            self.goto("findGoal",[self.p,self.t,self.z,self.r],dir)
            return
        self.robot.ptz[0].pan(pose[0] + self.speed)
        
class findGoal(State):
    def onActivate(self):
        self.speed = 0.05
        self.robot.move(0,0)
        self.headMaxTurn = 0.2
        self.strafeSpeed = 0.5
        self.turnSpeed = 0.1
        self.counter = 0
        print "FIND GOAL"

    def onGoto(self, args):
        self.robot.ptz[0].setPose(args[0])
        sleep(1)
        self.dir = args[1]
        if self.dir == 0:
            self.goto("prepareToKick")
    
        
    def step(self):
        self.robot.strafe(0)
        self.robot.move(0,0)
        areab = 0
        results = self.robot.camera[0].filterResults
        if len(results) > 1 and len(results[-1]) > 0: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a ball blob in sight
                x1b, y1b, x2b, y2b, areab = results[-1][0]
                centerXb, centerYb = (x1b + x2b)/2, (y1b + y2b)/2
        if len(results) > 1 and len(results[1]) > 0: # need a match, and blobify at least
            if len(results[1][0]) == 5: # have a goal blob in sight
                x1g, y1g, x2g, y2g, areag = results[1][0]
                centerXg, centerYg = (x1g + x2g)/2, (y1g + y2g)/2
        if areab > 10: #self.matchBall:
            # see the ball and search for the goal
            pose = self.robot.ptz[0].pose # p,t,z,r
            # 1. center camera on ball
            # ---------------X direction------------------
            diff = (centerXb - (self.robot.camera.width/2))
            if abs(diff) < (.1 * self.robot.camera.width):
                pass
            elif diff < 0:
                # negative is right, positive is left
                self.robot.ptz[0].pan( pose[0] + self.speed) 
            else:
                self.robot.ptz[0].pan( pose[0] - self.speed)
            # ---------------Y direction------------------
            # keep ball at the bottom of the image
            if y1b < (.5*self.robot.camera.width):
                self.robot.ptz[0].tilt( pose[1] + .5*self.speed) # up
            elif y1b > .8*self.robot.camera.width:
                # don't want to lose ball
                self.robot.ptz[0].tilt(pose[1] - .5*self.speed) # down
            # keep the ball centered
            if abs(pose[0]) > self.headMaxTurn:
                # 2.1 rotate so ball is in front of you
                if pose[0] > 0:
                    self.robot.move(0,self.turnSpeed)
                    self.robot.ptz[0].pan(pose[0] - self.speed)
                else:
                    self.robot.move(0,-self.turnSpeed)
                    self.robot.ptz[0].pan(pose[0] + self.speed)
            if areag> 10:#self.matchGoal:
                # if you see the goal
                diff = (centerXg - (self.robot.camera.width/2))
                if abs(diff) < (.1 * self.robot.camera.width):
                    # if centered on x direction
                    self.robot.strafe(0)
                    self.goto("prepareToKick")
                    return
            # rotate around the ball
            self.counter+=1
            print self.counter,
            self.robot.strafe(self.strafeSpeed*self.dir)
        else:
            self.robot.strafe(0)
            self.goto("searchDown")
                
class didYouScore(State):

    def onActivate(self):
        self.robot.move(0,0)
        self.robot.ptz[0].pan(0)
        self.robot.ptz[0].tilt(-0.1)
        self.speed = 0.05
        self.speedHor = 0.05
        self.tiltSpeed = 0.3
        print "DID YOU SCORE"
           
    def step(self):
        pose = self.robot.ptz[0].pose
        results = self.robot.camera[0].filterResults
        if len(results) > 1 and len(results[-1]) > 0: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a ball blob in sight
                x1b, y1b, x2b, y2b, areab = results[-1][0]
        if len(results) > 1 and len(results[1]) > 0: # need a match, and blobify at least
            if len(results[1][0]) == 5: # have a goal blob in sight
                x1g, y1g, x2g, y2g, areag = results[1][0]
        if areab> matchBall:
            if areag> matchGoal:
                if (y2g >= y2b) and \
                   ((x1b > x1g  and x1b < x2g) or (x2b < x2g and x2b> x1g)):
                    self.goto("moveTail")
                    return
            self.goto("waitForBall")
            return
        else:
            if (abs(pose[0]) > 0.6):
                self.speedHor = -self.speedHor
                if pose[1] <= -0.8:
                    self.goto("waitForBall")
                    return
                self.robot.ptz[0].tilt(pose[1] - self.tiltSpeed)
            self.robot.ptz[0].pan(pose[0] - self.speedHor)

class moveTail(State):
    def onActivate(self):
        self.robot.playSound("3yips")
        self.side = 1.0
        self.robot.setPose("tail",self.side, 0)
        self.counter = 1
        
    def step(self):
        self.side = -self.side
        self.robot.setPose("tail pan", self.side)
        self.counter +=1
        if self.counter > 25:
            self.goto("waitForBall")

class waitForBall(State):
    """
      The robot looks around for the ball and then waits until the ball is
      on its side of the court.
    """

    def onActivate(self):
        self.speed = 0.05
        self.speedHor = 0.05
        self.tiltSpeed = 0.3
        print "WAIT FOR BALL"
        
    def step(self):
        results = self.robot.camera[0].filterResults
        pose = self.robot.ptz[0].pose
        if len(results) > 1 and len(results[-1]) > 0: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a ball blob in sight
                x1b, y1b, x2b, y2b, areab = results[-1][0]
        if len(results) > 1 and len(results[1]) > 0: # need a match, and blobify at least
            if len(results[1][0]) == 5: # have a goal blob in sight
                x1g, y1g, x2g, y2g, areag = results[1][0]
        if areab> matchBall:
            # move the head so you can see the floor next to the ball
            if y2b > (.5*self.robot.camera.width):
                self.robot.ptz[0].tilt( pose[1] - .5*self.speed) # down
                if pose[1] < -0.8:
                    # cannot move head anymore
                    self.goto("approachBall")
                    return
            elif y2b < .2*self.robot.camera.width:
                # don't want to lose ball
                self.robot.ptz[0].tilt(pose[1] - .5*self.speed) # up
            else:
                if  areag> matchGoal:
                    if y2g < y2b or x2b < x1g or x1b > x2g:
                        self.goto("approachBall")
                        return
                else:
                    self.goto("approachBall")
                    return
        else:
            # search for the ball
            if (abs(pose[0]) == 1.0):
                self.speedHor = -self.speedHor
                if pose[1] >= 0 or pose[1] <= -0.8:
                    self.tiltSpeed = -self.tiltSpeed
                self.robot.ptz[0].tilt(pose[1] - self.tiltSpeed)
                
            self.robot.ptz[0].pan(pose[0] - self.speedHor)
                    
def INIT(engine):
    brain = RobotVsRobotSoccer(engine)
    brain.add(searchDown())
    brain.add(searchLeftRight())
    brain.add(searchRightLeft())
    brain.add(approachBall())
    brain.add(searchDynamic())
    brain.add(lostBall())
    brain.add(prepareToKick())
    brain.add(findGoal())
    brain.add(lookForGoal())
    brain.add(kick())
    brain.add(didYouScore())
    brain.add(moveTail())
    brain.add(waitForBall(1))
    return brain
    
