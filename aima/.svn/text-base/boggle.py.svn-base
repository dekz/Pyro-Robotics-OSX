"""Generate high-scoring boards in the game of Boggle.  A good domain for
iterative-repair and related search tehniques, as suggested by Justin Boyan."""

import random, time, bisect, math, string

##_____________________________________________________________________________

cubes16 = ['FORIXB', 'MOQABJ', 'GURILW', 'SETUPL',
           'CMPDAE', 'ACITAO', 'SLCRAE', 'ROMASH',
           'NODESW', 'HEFIYE', 'ONUDTK', 'TEVIGN',
           'ANEDVZ', 'PINESH', 'ABILYT', 'GKYLEU']

def random_board(n=4):
    "Return a random board of size n x n."
    cubes = [cubes16[i % 16] for i in range(n*n)]
    random.shuffle(cubes)
    return map(random.choice, cubes)

def board(str):
    "Return a board made from the letters in str."
    return [c.upper() for c in str if c in string.letters]

## The best 5x5 board found by Boyan, with our word list we get
## 2274 words, for a score of 9837
boyan_best = board('RSTCS DEIAE GNLRP EATES MSSID')

def print_board(board):
    n2 = len(board); n = exact_sqrt(n2)
    for i in range(n2):
        if i % n == 0: print
        if board[i] == 'Q': print 'Qu',
        else: print str(board[i]) + ' ',
    print
    
def compute_neighbors(n2, cache={}):
    if cache.get(n2):
        return cache.get(n2)
    n = exact_sqrt(n2)
    neighbors = [None] * n2
    for i in range(n2):
        neighbors[i] = []
        on_top = i < n
        on_bottom = i >= n2 - n
        on_left = i % n == 0
        on_right = (i+1) % n == 0
        if not on_top:
            neighbors[i].append(i - n)
            if not on_left:  neighbors[i].append(i - n - 1)
            if not on_right: neighbors[i].append(i - n + 1)
        if not on_bottom:
            neighbors[i].append(i + n) 
            if not on_left:  neighbors[i].append(i + n - 1)
            if not on_right: neighbors[i].append(i + n + 1)
        if not on_left: neighbors[i].append(i - 1) 
        if not on_right: neighbors[i].append(i + 1)
    cache[n2] = neighbors
    return neighbors

def exact_sqrt(n2):
    "If n2 is a perfect square, return its square root, else raise error."
    n = int(math.sqrt(n2))
    assert n * n == n2
    return n

##_____________________________________________________________________________

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

class Wordlist:
    """This class holds a list of words. You can use (word in wordlist)
    to check if a word is in the list, or wordlist.lookup(prefix)
    to see if prefix starts any of the words in the list."""
    def __init__(self, filename, min_len=3):
        lines = open(filename).read().upper().split()
        self.words = [word for word in lines if len(word) >= min_len]
        self.words.sort()
        self.bounds = {}
        for c in ALPHABET:
            c2 = chr(ord(c) + 1)
            self.bounds[c] = (bisect.bisect(self.words, c),
                              bisect.bisect(self.words, c2))

    def lookup(self, prefix, lo=0, hi=None):
        """See if prefix is in dictionary, as a full word or as a prefix.
        Return two values: the first is the lowest i such that
        words[i].startswith(prefix), or is None; the second is
        True iff prefix itslef is in the Wordlist."""
        words = self.words
        i = bisect.bisect_left(words, prefix, lo, hi)
        if i < len(words) and words[i].startswith(prefix): 
            return i, (words[i] == prefix)
        else: 
            return None, False

    def __contains__(self, word): 
        return self.words[bisect.bisect_left(self.words, word)] == word

    def __len__(self): 
        return len(self.words)
    
wordlist = Wordlist("../data/wordlist")

##_____________________________________________________________________________

class BoggleFinder:
    def __init__(self, wordlist=wordlist):
        self.wordlist = wordlist
        self.found = {}

    def set_board(self, board=None):
        if board is None:
            board = random_board()
        self.board = board
        self.neighbors = compute_neighbors(len(board))
        self.found = {}
        for i in range(len(board)):
            lo, hi = self.wordlist.bounds[board[i]]
            self.find(lo, hi, i, [], '')
        return self
            
    def find(self, lo, hi, i, visited, prefix):
        if i in visited: 
            return
        wordpos, is_word = self.wordlist.lookup(prefix, lo, hi)
        if wordpos is not None:
            if is_word: 
                self.found[prefix] = True
            visited.append(i)
            c = self.board[i]
            if c == 'Q': c = 'QU'
            prefix += c
            for j in self.neighbors[i]: 
                self.find(wordpos, hi, j, visited, prefix)
            visited.pop()
                                    
    def count(self): 
        return len(self.found)

    def words(self): 
        return self.found.keys()

    scores = [0, 0, 0, 0, 1, 2, 3, 5] + [11] * 100

    def score(self):
        return sum([self.scores[len(w)] for w in self.words()])

    def __len__(self):
        return len(self.found)

##_____________________________________________________________________________
    
def boggle_hill_climbing(n=5, ntimes=1000, print_it=True):
    finder = BoggleFinder()
    board, best = random_board(n), 0
    for _ in range(ntimes):
        i, c = mutate(board)
        new = len(finder.set_board(board))
        if new > best:
            print best, new
            best = new
        else:
            board[i] = c ## Change back
    if print_it:
        print_board(board)
    return board, best

def mutate(board):
    i = random.randrange(len(board))
    #c = random.choice(random.choice(cubes16))
    c = random.choice(boyan_best)
    board[i] = c
    return i, c
