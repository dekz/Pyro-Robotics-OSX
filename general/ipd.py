# D.S. Blank
# Emergence, Spring 2004
# Bryn Mawr College

from random import random
import operator, os, sys

class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

    def play(self, rounds):
        self.player1.__init__()
        self.player2.__init__()
        print "================================================"
        print self.player1.__class__.__name__, "vs",
        print self.player2.__class__.__name__
        self.score1 = 0
        self.score2 = 0
        for i in range(rounds):
            self.playOne()
        if self.score1 > self.score2:
            print "Player 1", self.player1.__class__.__name__, "wins!"
        elif self.score2 > self.score1:
            print "Player 2", self.player2.__class__.__name__, "wins!"
        else:
            print "Tie game!"
        print "Player1:", self.player1.getHistory()
        return self.score1/float(rounds), self.score2/float(rounds)

    def playOne(self):
        p1 = self.player1.play()
        p2 = self.player2.play()
        self.player1.history.append( (p1, p2) )
        self.player2.history.append( (p2, p1) )
        if (p1, p2) == ("D", "C"):
            self.score1 += 5
            self.score2 += 0
        elif (p1, p2) == ("C", "D"):
            self.score1 += 0
            self.score2 += 5
        elif (p1, p2) == ("D", "D"):
            self.score1 += 1
            self.score2 += 1
        elif (p1, p2) == ("C", "C"):
            self.score1 += 3
            self.score2 += 3
        else:
            raise AttributeError, "invalid play"


class Player:
    def __init__(self):
        self.history = []
    def getHistory(self):
        return reduce(operator.add, map(lambda pair: pair[0] + pair[1] + ",", self.history))

class AlwaysDefect(Player):
    def play(self):
        return "D"

class AlwaysCooperate(Player):
    def play(self):
        return "C"

class RandomPlayer(Player):
    def play(self):
        return "CD"[int(random() * 2)]

class TitForTat(Player):
    def play(self):
        if len(self.history) == 0:
            return "C"
        else:
            return self.history[-1][1]

players = (AlwaysDefect(), RandomPlayer(), AlwaysCooperate(), TitForTat())

files = os.popen("ls /home/*/ipd.py")
sys.path.insert(0, '')
for file in files:
    file = file.strip()
    path = file[:-6]
    sys.path[0] = path
    import ipd as userspace
    reload(userspace)
    IPD = userspace.IPD
    players.append( IPD() )
    
for i in players:
    for j in players:
        game = Game(i, j)
        print game.play(50)
