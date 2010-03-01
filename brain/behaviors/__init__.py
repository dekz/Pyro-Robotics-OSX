# This is basically a rewrite of XRCL in Python
# BehaviorBased Brain

# defines the Behavior-based brain, behaviors, and states
import time
from pyrobot.brain import Brain

class BehaviorBasedBrain(Brain):
   """
   This is the main engine that runs collections of behaviors (states).
   Usually, you create once of these per robot.
   """
   def __init__(self, controllers = {}, engine = 0, **args):
      Brain.__init__(self, 'BehaviorBasedBrain', engine, **args)
      self.states = {}
      self.controls = controllers
      self.history = [{}, {}, {}]
      self.pie = []
      self.desires = []
      self.effectsTotal = {}
      self.initialized = 0
      self.activeState = None
   def getStates(self, status = 1):
      return [state.name for state in self.states.values() if state.status == status]
   def set_controls(self, controllers):
      self.controls = controllers
      self.history = [{}, {}, {}]
   def activate(self, name):
      self.states[name].status = 1
      self.states[name].onActivate()
      self.goto(name)
   def goto(self, name):
      self.activeState = self.states[name]
   def deactivate(self, name):
      self.states[name].status = 0
      self.states[name].onDeactivate()
      self.activeState = None
   def add(self, state):
      if state.name in self.states.keys():
         raise "ERROR: state already exists: '" + state.name + "'"
      self.states[state.name] = state
      state.engine = self.engine
      state.robot = self.engine.robot
      state.brain = self
      state.setup()
      if state.status:
         state.onActivate()
   def reset(self):
      self.states = {}
      #self.status = -1
      self.desires = []
      self.effectsTotal = {}
   def step(self):
      if not self.initialized:
         for s in self.states.keys():
            self.states[s].setcontrols(self.controls)
         self.initialized = 1
      self.desires = [] # init all desires (this will be set in state.run)
      self.history[2] = self.history[1]
      self.history[1] = self.history[0]
      self.history[0] = {}
      self.effectsTotal = {}
      for s in self.states.keys():
         if self.states[s].status == 1:
            self.states[s].run()
      # desires: truth, controller, value, rulename, behname, statename
      control = {}
      # set all totalTruths to 0, totalEffects to 0
      totalTruth = {}
      totalEffects = {}
      for c in self.controls.keys():
         totalTruth[c] = 0.0
         totalEffects[c] = 0.0
      for e in self.effectsTotal.keys(): # state:beh:controller
         s, b, c = e.split(':')
         totalEffects[c] = max(float(self.effectsTotal[e]), totalEffects[c])
      # sum up totalTruth
      for d in self.desires: 
         # compute total truth for each controller
         totalTruth[d[1]] += d[0] * (self.effectsTotal[d[5]+":"+d[4]+":"+d[1]] / totalEffects[d[1]])
      self.pie = []
      for d in self.desires: 
         # (beffect / totaleffect) * (truth / totaltruth) * value
         c = d[1]
         if totalTruth[c] != 0:
            part = ((d[0]*(self.effectsTotal[d[5]+":"+d[4]+":"+d[1]]/totalEffects[d[1]]))/totalTruth[c])
         else:
            part = 0
         amt = part * d[2]
         self.pie.append( [d[1], (self.effectsTotal[d[5] + ":" + d[4] + ":" + c] / totalEffects[c]),
                           part, d[2], amt,
                           d[5] + ":" + d[4] + ":" + d[3] ] )
         if c in control.keys():
            control[c] += amt
         else:
            control[c] = amt
      for c in self.controls.keys():
         if c in control.keys():
            # set that controller to act with a value
            #print "setting %s to value %f" % (c, control[c])
            self.controls[c](control[c])
            self.history[0][c] = control[c]
      # -------------------------------------------------
      # This will update robot's position so that the GUI
      # can draw it, even if no command is sent to move
      # the robot. 
      # -------------------------------------------------
      self.controls['update']()
      # -------------------------------------------------
      # let's force a 0.1s break so that we are going to have
      # at most 10 cycles per second
      # an improved version is expected
      # -------------------------------------------------
      time.sleep(0.01)
      # change states' status if necessary
      for s in self.states.keys():
         for d in self.states[s].deactivatelist: #deactivate first
            self.deactivate(d)
         for a in self.states[s].activatelist:
            self.activate(a)
         self.states[s].activatelist = []
         self.states[s].deactivatelist = []
   def stop_all(self):
      for c in self.controls.keys():
         # set that controller to act with a value
         self.controls[c](0)
   def redrawPie(self, pie, percentSoFar, piececnt, controller,
                 percent, name):
      # FIX: behavior specific. How to put in Behavior-based code?
      xoffset = 5
      yoffset = 20
      width = 100
      row = (pie - 1) * (width * 1.5)
      colors = ['blue', 'red', 'tan', 'yellow', 'orange', 'black', 'azure', 'beige', 'brown', 'coral', 'gold', 'ivory', 'moccasin', 'navy', 'salmon', 'tan', 'ivory']
      self.canvas.create_text(xoffset + 60,row + 10, tags='pie',fill='black', text = controller) 
      self.canvas.create_arc(xoffset + 10,row + yoffset,width + xoffset + 10,row + width + yoffset,start = percentSoFar * 360.0, extent = percent * 360.0 - .001, tags='pie',fill=colors[(piececnt - 1) % 17])
      self.canvas.create_text(xoffset + 300,row + 10 + piececnt * 20, tags='pie',fill=colors[(piececnt - 1) % 17], text = name)

   def redraw(self):
      if len(self.pie) != 0:
         self.canvas.delete('pie')
         piecnt = 0
         for control in self.controls:
            if control == "update": continue
            piecnt += 1
            percentSoFar = 0
            piececnt = 0
            for d in self.pie:
               if control == d[0]:
                  piececnt += 1
                  portion = d[2]
                  #try:
                  self.redrawPie(piecnt, percentSoFar, \
                                 piececnt, \
                                 "%s effects: %.2f" % \
                                 (d[0], self.history[0][d[0]]),
                                 portion, \
                                 "(%.2f) %s IF %.2f THEN %.2f = %.2f" % \
                                 (d[1], d[5], d[2], d[3], d[4]))
                  #except:
                  #     pass
                  percentSoFar += portion
      else:
         if getattr(self, 'canvas', None) is not None:
            self.canvas.create_text(200,130, tags='pie',fill='black', text = "Ready...")

class Behavior:
   """
   The core object. This gets subclassed for each beh instance
   """
   def __init__(self, status = 0, effects = {}, name = ''):
      self.status = status
      self.type = self.__class__.__name__
      self.name = name or self.type
      self.effects = effects
      self.robot = 0 # filled in later
      self.brain = 0 # filled in later
      self.engine = 0 # filled in later
   def setup(self):
      pass # this will get over written, normally
   def onActivate(self):
      pass
   def onDeactivate(self):
      pass
   def update(self):
      pass # this will get over written, normally
   def Effects(self, controller, amount = 1.0):
      self.effects[controller] = amount
   def IF(self, fvalue, controller, amount = 1.0, name = ''):
      if name == '':
         name = "Rule%d" % (len(self.rules) + 1)
      self.rules.append([float(fvalue), controller, float(amount), name])

class FSMBrain(BehaviorBasedBrain):
   """
   This is the main engine that runs the FSM.
   """
   def activate(self, name):
      self.states[name].status = 1
      self.states[name].onActivate()

   def deactivate(self, name):
      self.states[name].status = 0
      self.states[name].onDeactivate()

   def reset(self):
      self.states = {}

   def step(self):
      for s in self.states.keys():
         if self.states[s].status == 1:
            self.states[s].run()
      # pause?
      for s in self.states.keys():
         for d in self.states[s].deactivatelist: #deactivate first
            self.deactivate(d)
         for a in self.states[s].activatelist:
            self.activate(a)
         self.states[s].activatelist = []
         self.states[s].deactivatelist = []

class State:
   """
   Collections of behaviors. this gets subclassed by each collection
   """
   def __init__(self, status = 0, name = ''):
      self.debug = 0
      self.behaviors = {}
      self.activatelist = []
      self.deactivatelist = []
      self.status = status
      self.type = self.__class__.__name__
      self.name = name or self.type

   def getState(self, statename):
      if statename in self.brain.states.keys():
         return self.brain.states[statename]
      else:
         raise "ERROR: no such statename"
   def goto(self, state, *args):
      if self.debug:
         print "Leaving state '%s'; going to state '%s'..." % (self.name, state)
      self.deactivate(self.name)
      self.activate(state)
      self.brain.states[state].onGoto(args)
      self.brain.goto(state)
   def onGoto(self, args = []):
      # FIX: could make a nice way of setting class vars here.
      # Currently:
      # if you pass this vars, you must take care of them!
      pass # normally will overload
   def activate(self, name):
      if not (name in self.activatelist):
         self.activatelist.append(name)
   def deactivate(self, name):
      if not (name in self.deactivatelist):
         self.deactivatelist.append(name)
   def onActivate(self):
      pass
   def setup(self):
      pass # normally will overload
   def onDeactivate(self):
      pass # normally will overload
   def update(self):
      self.step()
   def step(self):
      pass # normally will overload
   def add(self, b):
      if b.name in self.behaviors.keys():
         raise "ERROR: beh already exists: '" + b.name + "'"
      else:
         self.behaviors[b.name] = b
      # keep a pointer to parent engine, from the beh:
      b.engine = self.engine
      b.brain = self.engine.brain
      b.robot = self.engine.robot
      # keep a pointer to parent state, from the beh:
      b.state = self
      b.setup() # init the behavior, just once
      if b.status:
         print "Activating state '%s'..." % b.name
         b.onActivate()
   def setcontrols(self, controls):
      self.controls = controls
   def run(self):
      for bkey in self.behaviors.keys():
         b = self.behaviors[bkey]
         if b.status:
            b.rules = [] # clear rules
            b.update() # fires IF rules
            for r in b.rules:
               # r = truth, controller, amount, beh name, state name
               r.extend([b.name, b.state.name])
               self.brain.desires.append( r )
               # what is the controller effect for this state/behavior?
               self.brain.effectsTotal[b.state.name+":"+b.name+":"+r[1]] = b.effects[r[1]]
      self.update()

   def push(self, statename = None):
      if statename == None:
         statename = self.name
      if statename not in self.brain.states:
         raise AttributeError, "push: not a valid state name '%s'" % statename
      self.brain.stack.append( statename )

   def pop(self):
      if len(self.brain.stack) > 0:
         returnState = self.brain.stack.pop()
         self.goto(returnState)
      else:
         raise AttributeError, "pop without a push in state '%s'" % self.name

   # wrappers here to talk to default robot:
   def move(self, *args):
      return self.robot.move(*args)
   def translate(self, *args):
      return self.robot.translate(*args)
   def rotate(self, *args):
      return self.robot.rotate(*args)
   def stop(self):
      return self.robot.stop()
   def startDevice(self, *args, **keywords):
      return self.robot.startDevice(*args, **keywords)
   def removeDevice(self, *args, **keywords):
      return self.robot.removeDevice(*args, **keywords)
   def motors(self, *args):
      return self.robot.motors(*args)
   def getDevice(self, *args):
      return self.robot.getDevice(*args)
   def hasA(self, *args):
      return self.robot.hasA(*args)
   def requires(self, *args):
      return self.robot.requires(*args)

