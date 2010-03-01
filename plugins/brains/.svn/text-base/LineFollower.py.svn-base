# Simple Line Follower

from pyrobot.brain import Brain  
   
class LineFollower(Brain):
   lastLeft = 1
   lastRight = 1
        
   def setup(self):
   	self.robot.setRangeSensor("light", 0)

   # Give the front two sensors, decide the next move  
   def determineMove(self, left, right):
		
   	if (left <= .9) and (right <= .9):
        	print "On track"
         	return(.3, 0)  
    	elif (left <= .9) and (right > .9): 
        	print "line detected on Left, slow turn to left"
        	return(.1, .2)
   	elif (left > .9) and (right <= .9):
      		print "line detected on right, slow turn to right"
		return(.1, -.2)
    	else:   
		print "No line detected, attempting to locate line depending on last movements"
        	if self.lastLeft <= .9:
			return(.1, .2)
		elif self.lastRight <= .9:
			return(.1, -.2)
		else:
			print "Last location tests failed, beginning circular search"
			return(0, .3)
	self.lasLeft = left
	self.lastRight = right 
			
   def step(self):  
   	left = min([s.distance() for s in self.robot.range["left-front"]])
   	right = min([s.distance() for s in self.robot.range["right-front"]])
     	translation, rotate = self.determineMove(left, right)  
	self.robot.move(translation, rotate)

def INIT(engine):  
	assert (engine.robot.requires("range-sensor") and
		engine.robot.requires("continuous-movement"))
	return LineFollower('LineFollower', engine)
	
