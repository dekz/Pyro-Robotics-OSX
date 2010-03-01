"""
----------------------------------------------------
A temporal differencing backprop. Part of the
Pyrobot Robotics Project.
Provided under the GNU General Public License.
----------------------------------------------------
(c) 2001-2005, Developmental Robotics Research Group
----------------------------------------------------

This file implements the major classes and functions for
performing Temporal Differencing in Python. Part of the
Pyrobot project.
"""

__author__ = "Robert Casey <rcasey@cs.uml.edu>"
__version__ = "$Revision$"

from Numeric import resize
import itertools

class Temporal_Difference:
    """
    Class which contains Utility Values and performs operations on them
    """
    # constructor
    def __init__(self, sizex, sizey, goal, pits, alpha=0.2):
        self.goal = goal
        self.pits = pits

        self.num_squares_x = sizex
        self.num_squares_y = sizey
        self.alpha = alpha
        
        # self.utility     = resize( 0.0,(self.num_squares_x,self.num_squares_y)); 
        self.reset_utils()
        # self.reward      = resize( 0.0,(self.num_squares_x,self.num_squares_y)); 
        self.reset_reward()
        # self.frequencies = resize(   0,(self.num_squares_x,self.num_squares_y));
        self.reset_frequencies()
        

        
    def reset_utils(self):
        self.utility = resize(0.0,(self.num_squares_x,self.num_squares_y)); 

        for e in self.pits:
            self.utility[e] = -1.0
        e = self.goal
        self.utility[e] = 1.0

    def reset_reward(self):
        self.reward = resize(0.0,(self.num_squares_x,self.num_squares_y))

        self.reward[self.goal] = 100
        for e in self.pits:
            self.reward[e] = -50

    def reset_frequencies(self):
        self.frequencies = resize(0,(self.num_squares_x,self.num_squares_y))

    def get_alpha( self ):
        return self.alpha
    
    def set_alpha( self, new_val ):
        self.alpha = new_val
        
    def running_average( self, util, reward, freq ):
        return ((util * (freq - 1) + reward) / freq)
   
    def do_td( self, p ):
        U = self.utility
        frequencies = self.frequencies
        final_states = self.pits + [self.goal]

        # we want to traverse in reverse!
        p.reverse();
        next_state = p[0]
        # start from end, go until start
        for curr_state in p:
            # update the frequencies of all states in the path
            frequencies[curr_state] = frequencies[curr_state] + 1
            
            if( curr_state in final_states ):
                rew = self.reward[curr_state] - (len(p) * 0) # 2)
                U[curr_state] = round( self.running_average( U[curr_state],
                                                            self.reward[curr_state],
                                                            frequencies[curr_state] ), 10) ;
            else:
                temp = U[next_state]-U[curr_state];
                U[curr_state] = round(U[curr_state] + self.alpha*(self.reward[curr_state] + temp), 10);
                
            # since we're iterating backwards
            next_state = curr_state;

        self.frequencies = frequencies
        self.utility = U

    def get_utility( self, x, y ):
        return self.utility[x][y]


    # returns an RGB string for a given utility value
    def get_utility_color(self, x, y):
        util = self.utility[x][y]

        if util < 0:
            neg = 1
            util *= -1
        else:
            neg = 0

        r = 255
        g = 255 - int( util * 2.55 )
        b = 255 - ( int( util * 2.55 ) * 2 )

        if b < 0:
            b = 0
            
#        print "%d:%d:%d" % ( r,g,b )

        if neg:
            tmp = b
            b = r
            r = tmp

        strr = hex(r)[2:]
        while len(strr) < 2:
            strr = "0" + strr;
        strg = hex(g)[2:]
        while len(strg) < 2:
            strg = "0" + strg;
        strb = hex(b)[2:]
        while len(strb) < 2:
            strb = "0" + strb;


        strcolor = "#" + strr + strg + strb
        return( "c_%2d%2d_%s" % (x, y, strcolor) )
    
