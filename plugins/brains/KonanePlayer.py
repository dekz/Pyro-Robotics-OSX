"""
This module contains a class of a random Konane Player.
The brain KonanePlayer program plays a random game of Konane.
"""

from pyrobot.brain import Brain
import time, random

def otherPiece(piece):
    """ What is the opponent's shape? """
    if piece == 'O': return 'X'
    else: return 'O'

def getEmpties(board):
    """ Returns all of the empty positions on board. """
    retval = []
    for i in range(8):
        for j in range(8):
            if board[i][j] == '':
                retval.append( (i+1, j+1) )
    return retval

def add(pos, offset):
    """ Adds two board positions together """
    return (pos[0] + offset[0], pos[1] + offset[1])

def validPos(pos, offset = (0,0)):
    """ Is this position + offset a valid board position?"""
    newx, newy = add(pos, offset)
    return (newx >= 1 and newx <= 8 and newy >= 1 and newy <= 8)

def moveGenerator(board, myPiece, firstMove):
    """Generates legal board moves. Doesn't find multiple-jumps. """
    retval = []
    empties = getEmpties(board)
    if firstMove:
        if len(empties) == 0: # I'm first!
            if myPiece == "O":
                retval.extend( [(4,4), (5,5), (1,1), (8,8)] )
            else:
                retval.extend( [(5,4), (4,5), (1,8), (8,1)] )
        else: # I'm second
            # get one of the 4 (or less) surrounding pieces
            openPos = empties[0] # better be just one
            for i,j in [(-1,0), (+1,0), (0, -1), (0, +1)]:
                if validPos(openPos, (i,j)):
                    retval.append( add(openPos, (i,j)) )
    else:
        # find all moves, and add them to list
        for i in range(1,9):
            for j in range(1,9):
                if board[i-1][j-1] == myPiece:
                    for a,b in [(0, -2),(+2,-2), (+2, 0),(+2, +2),
                                (0, +2),(-2, +2),(-2, 0),(-2, -2)]:
                        p, q = i, j   # a starting place
                        move = [i, j] # first part of move
                        while 1: # still jumps to make
                            if validPos((p,q), (a,b)):
                                x,y = add((p,q),(a,b))
                                if board[x-1][y-1] == '':
                                    bx, by = add( (p,q), (x,y) )
                                    bx, by = bx/2, by/2
                                    if board[bx-1][by-1] == otherPiece(myPiece):
                                        move.extend( [x,y] )
                                        # jump some more?
                                        p, q = x, y
                                    else:
                                        break
                                else:
                                    break
                            else:
                                break
                        if len(move) > 2:
                            retval.append( move )
    return retval

def formatMove(move):
    """ Formats a list of positions into a jump() string. """
    movestr = "jump(%d,%d" % (move[0], move[1])
    while 1:
        x1, y1, x2, y2 = move[:4]
        movestr += ",%d,%d" % (x2, y2)
        move = move[2:]
        if len(move) < 4:
            break
    movestr += ")"
    return movestr

class KonanePlayer(Brain):
    """
    A simple Random Konane Player. Note that the rep of board is
    zero-based, but all other places is one's based.
    For use with PyrobotSimulator and KonaneWorld.py and
    PyrobotRobot.py (a TCPRobot from pyrobot/robot/symbolic.py)
    """
    def setup(self):
        if self.robot.id == 0:
            self.myPiece = "O"
        else:
            self.myPiece = "X"
        self.firstMove = 1
        self.turn = 1
        print "Welcome to Konane, Hawaiian Checkers!"
        print "Red O or X on the board indicates that it"
        print "is that shape's move."
        print "Jumps must occur in a straight line."
        print "A human can play, or start two Pyrobot's up,"
        print "and connect onto two different ports using"
        print "PyrobotRobot60000 and PyrobotRobot60001."

    def step(self):
        if self.robot.whosMove != self.robot.id:
            time.sleep(1)
            return
        board = self.robot.board
        moves = moveGenerator(board, self.myPiece, self.firstMove)
        self.firstMove = 0
        if len(moves) > 0:
            # Here is where you would go through the possible
            # moves and pick the best one.
            # I'm just going to pick a random one:
            move = moves[int(len(moves) * random.random())]
            if len(move) == 2: # remove the piece
                self.robot.play("remove(%d,%d)" % move)
                print self.turn, "remove(%d,%d)" % move
                self.robot.play("done")
            else: # jumps
                movestr = formatMove(move)
                print self.turn, movestr
                self.robot.play(movestr)
                self.robot.play("done")
            self.turn += 1
        else:
            print "You win!"
            self.pleaseStop() # request to stop running brain

def INIT(engine):
    return KonanePlayer("Random Konane Player", engine)
