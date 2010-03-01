from pyrobot.brain import Brain
from pyrobot.robot.rovio import *

class rovioTrackBall(Brain):

    def setup(self):
        self.cam = self.robot.camera[0]
        self.cam.addFilter("match", 255, 77, 85)
        self.cam.addFilter("match", 254, 121, 155)
        self.cam.addFilter("blobify",0,255,255,0,1,1,1,)
        print "setup complete"
                
    def destroy(self):
        self.cam.clearFilters()

    def redraw(self):
        pass

    def step(self):
        self.robot.ping()
        results = self.robot.camera[0].filterResults
        print results
        if len(results) > 1 and len(results[-1]) > 0: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a blob in sight
                x1, y1, x2, y2, area = results[-1][0]
                if area > 25:
                    centerX, centerY = (x1 + x2)/2, (y1 + y2)/2
                    diff = (centerX - (self.cam.width/2))
                    if abs(diff) < (.2 * self.cam.width):
                        self.robot.translate(1)
                    elif diff < 0:
                        # negative is right, positive is left
                        print "Turn Left"
                        self.robot.rotate(.3) 
                        self.robot.rotate(.3) 
                    else:
                        print "Turn Right"
                        self.robot.rotate(-.3) 
                        self.robot.rotate(-.3) 
                    # ---------------------------------
                    diff = (centerY - self.cam.height/2) 
                    if abs(diff) < .1 * self.cam.height:
                        pass
                    elif diff < 0: # down
                        self.robot.headPos(1)
                    elif diff > .3 * self.cam.height:
                        self.robot.headPos(2)
                    
                else:
                    pass
                  #self.robot.move(1,0)
                
            else:
                pass
              #self.robot.rotate(-.7)

def INIT(engine):
    return rovioTrackBall("Tracker", engine)
      
