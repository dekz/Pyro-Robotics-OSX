from pyrobot.brain import Brain
from time import sleep
from random import *
from pyrobot.brain.td import *

class SimpleBrain(Brain):

   random_percent = 20
   reset = 0

   # reinforcement value for temporal differencing
   REINFORCEMENT_VALUE = .2
   
   # just calls find_successor
   def find_path( self ):
      loc = self.robot.ask('location')

      # make sure we got a tuple
      if type(loc) != type( () ):
         return "";
         
      direction = self.find_successor(loc)
      return direction

   # finds the next step, by random, utility-based, or direct moves
   def find_successor( self, loc ):
      valid_state = 0

      moves = self.get_valid_moves( loc )
      
      if not moves:
         path = self.robot.ask('path')
         cx, cy = loc
         px, py = path[len(path) - 2]

         if px==cx:
            if py < cy:
               return "up"
            else:
               return "down"
         else:
            if px < cx:
               return "left"
            else:
               return "right"
      else:
         move_type = randrange(0, 100, 1)
         if move_type < self.random_percent:  # chance of random movement
            return moves[ randrange(0,len(moves)) ]
         else:
            return self.util_successor( loc, moves )
      
      
   # returns the next location, based on utility values
   def util_successor( self, loc, valid_moves ):

      # best move will be the move with the highest utility value
      best_move = "none"
      zero_count = 0
      max_util = -999

      for m in valid_moves:
         # get the state
         new_state = self.valid_move( m, loc )

         # if we get a valid state, check to see if its the best one yet
         if new_state != 0:
            util = self.get_util( new_state )
            if util == 0.0:
               zero_count += 1

            if util > max_util:
               max_util = util
               best_move = m

      # make sure we aren't all zero
      if max_util == 0 and zero_count == len(valid_moves):
         return valid_moves[ randrange(0,len(valid_moves)) ]                     
      # make the move
      elif best_move != "none":
         return best_move
      else:
         # should NEVER get here, but just in case!
         print "NO GOOD SUCCESSOR FOUND"
         return valid_moves[ randrange(0,len(valid_moves)) ]            



   def get_valid_moves( self, loc ):
      valid = []
      states = ("up", "down", "left", "right") 

      for s in states:
         if self.valid_move( s, loc ):
            valid.append( s )

      return valid


   #checks to make sure that a move is valid
   def valid_move ( self, move, loc ):
      (locX, locY) = loc
      visited = self.robot.ask('visited')
      
      if move == "up":
         new_state = (locX  , locY - 1)
      elif move == "right":
         new_state = (locX+1, locY)
      elif move == "down":
         new_state  = (locX  , locY + 1)
      elif move == "left":
         new_state = (locX-1, locY)

      # if the new state is onto an obstacle, return 0
      if new_state in self.obstacles:
         return 0
      # if the new state is off the map, return 0
      elif min(new_state) < 0 or max(new_state) > 14:
         return 0
      elif new_state in visited:
         return 0
      else:
         return new_state
      
   # returns the utility value for a given location
   def get_util( self, loc ):
      #utils = self.robot.ask('util')
      (locX,locY) = loc

      if locX < 0 or locX > 14 or locY < 0 or locY > 14:
         return -99
      else:
         return self.td.get_utility(locX, locY)
     
   # gets called before first run
   def setup(self, **args):
      # set reinforcement value
      alpha = self.REINFORCEMENT_VALUE
      # get td instance
      self.td = Temporal_Difference( 15, 15, self.robot.ask('goal'), self.robot.ask('pits'), alpha )

      self.obstacles = self.robot.ask("obstacles")

      # initialize the number of iterations to zero
      self.count = 0

   # run once every iteration
   def step(self):
      if self.reset == 1:
         self.robot.tell("reset")
         self.robot.tell("start")
         self.setup()
         self.reset = 0

      # if the goal has not been reached, continue to find a path
      if self.robot.ask('complete') == 0:
         direction = self.find_path()
         self.robot.move( direction )

      # if the goal has been reached, display the current path
      else:
         path = self.robot.ask('path')
         self.count += 1

         # show the path
         print "PATH: ", path

         # adjust the utility values of the map
         print "Computing TDs: #", self.count, " length: ", len(path)
         self.td.do_td( path )

         # start a new run
         self.robot.tell('start')
         for e in path:
            # sends the robot a formatted string including the x,y coordinates, and a color
            self.robot.tell( self.td.get_utility_color(e[0], e[1]));

         alpha = self.td.get_alpha()
         if( (self.count % 15) == 0 and alpha > 0 ):
             self.td.set_alpha( alpha - 0.01 )
             self.random_percent -= 5

# -------------------------------------------------------
# This is the interface for calling from the gui engine.
# Takes one param (an engine), and returns a Brain object:
# -------------------------------------------------------

def INIT(engine):
   return SimpleBrain('SimpleBrain', engine)
