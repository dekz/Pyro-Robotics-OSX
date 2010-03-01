from pyrobot.brain import Brain

class TrackBall(Brain):

    def setup(self):
        self.cam = self.robot.camera[0]
        self.ptz = self.robot.ptz[0]
        self.ptz.setPose(0, 0, 0)
        #self.cam.addFilter("matchList", 229, 68, 164, 234, 18, 129, 0)
        self.cam.addFilter("match", 229, 68, 164)
        self.cam.addFilter("match", 234, 18, 129)
        self.cam.addFilter("blobify",0,255,255,0,1,1,1,)
                
    def destroy(self):
        self.cam.clearFilters()

    def step(self):
        results = self.robot.camera[0].filterResults
        if len(results) > 1 and len(results[-1]) > 0: # need a match, and blobify at least
            if len(results[-1][0]) == 5: # have a blob in sight
                x1, y1, x2, y2, area = results[-1][0]
                if area > 25:
                    centerX, centerY = (x1 + x2)/2, (y1 + y2)/2
                    pose = self.ptz.pose # p,t,z,r
                    #print "center:", (centerX, centerY)
                    # ---------------------------------
                    diff = (centerX - (self.cam.width/2))
                    if abs(diff) < (.1 * self.cam.width):
                        pass
                    elif diff < 0:
                        # negative is right, positive is left
                        self.ptz.pan( pose[0] + .05) 
                    else:
                        self.ptz.pan( pose[0] - .05) 
                    # ---------------------------------
                    diff = (centerY - self.cam.height/2) 
                    if abs(diff) < .1 * self.cam.height:
                        pass
                    elif diff < 0: # down
                        self.ptz.tilt( pose[1] + .05) # positive is left
                    else:
                        self.ptz.tilt( pose[1] - .05) # negative is right
                    
                else:
                    self.ptz.center() #print "searching..."
                
            else:
                self.ptz.center() #print "searching..."

def INIT(engine):
    engine.robot.requires("ptz")
    engine.robot.requires("camera")
    return TrackBall("Tracker", engine)
      
