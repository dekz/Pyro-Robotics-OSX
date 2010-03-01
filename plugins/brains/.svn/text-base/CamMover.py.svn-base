from pyrobot.brain import Brain

class SimpleBrain(Brain):
   # Only method you have to define is the step method:
   def step(self):
        pass

# -------------------------------------------------------
# This is the interface for calling from the loader.
# Takes one param (an engine), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain('SimpleBrain', engine)
      
