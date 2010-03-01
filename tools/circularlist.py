class CircularList:
    """

    A CircularList will store up to maxSize items. A size of -1
    indicates that the list has no maxSize.  Use the addItem method to
    insert an item into the list.  It will automatically remove the
    oldest item in the list if it has reached the maxSize.  Use the
    nextItem method to retrieve the oldest visited item. Use the
    __getitem__ method (object[item]) to retrieve an item at a
    particular index.
    
    """
    def __init__(self, size=-1):
        self.maxSize = size
        self.nextPos = 0
        self.contents = []
        self.names = []
        self.nextID = 0

    def __str__(self):
        output = ""
        if len(self.contents) == 0:
            return output + "Empty"
        output += "| "
        for i in range(len(self.contents)):
            if i == self.nextPos:
                output += " ^ "
            output += (str(self.contents[i]) + " ")
        return output + " |"

    def __len__(self):
        return len(self.contents)

    def __getitem__(self, index):
        if index >= 0 and index < len(self.contents):
            return self.contents[index]
        raise StopIteration, "no item at index %d in CircularList" % index

    def __iter__(self):
        for c in self.contents:
            yield c

    def addItem(self, item):
        if self.maxSize == 0: return
        if len(self.contents) == self.maxSize:
            self.contents.pop(0)
            self.names.pop(0)
        self.contents.append(item)
        self.names.append(self.nextID)
        self.nextID += 1

    def next(self):
        return self.nextItem()

    def nextItem(self):
        if len(self.contents) == 0:
            raise AttributeError, "no nextItem in empty CircularList"
        item = self.contents[self.nextPos]
        self.nextPos = (self.nextPos + 1) % len(self.contents)
        return item

def main():
    print "-------------------------------------------------"
    print "TEST: try to get the next item from an empty list"
    emptyList = CircularList()
    print emptyList
    try:
        emptyList.next()
        print "ERROR: did not catch the error"
    except:
        print "successfully caught the error"
    print "-------------------------------------------------"
    print "TEST: try to get a particular item from an empty list"
    try:
        emptyList[4]
    except:
        print "successfully caught the error"
    print "-------------------------------------------------"
    print "TEST: create a list with a maximum size of 5"
    clist = CircularList(5)
    for i in range(5):
        clist.addItem(i)
    print clist
    for i in range(len(clist)):
        print clist.next()
        print clist
    for i in range(3):
        clist.addItem(i*10)
    print clist
    print "Getting item at index two: ", clist[2]
    print "-------------------------------------------------"
    print "TEST: create a list with no maximum size"
    clist = CircularList()
    for i in range(5):
        clist.addItem(i)
    print clist
    for i in range(len(clist)):
        print clist.next()
        print clist
    for i in range(3):
        clist.addItem(i*10)
    print clist
    print "-------------------------------------------------"
    print "TEST: create a circular list of cicular lists"
    clist = CircularList()
    clist.addItem(CircularList(3))
    clist[0].addItem('a')
    clist[0].addItem('b')
    clist.addItem(CircularList(3))
    clist[1].addItem('c')
    clist.addItem(CircularList(3))
    clist[2].addItem('d')
    clist[2].addItem('e')
    clist[2].addItem('f')
    for i in range(12):
        print clist
        print "Next:", clist.next().next()
    print clist
    print "-------------------------------------------------"
    print "TEST: test circular list as an iterator"
    n = 0
    print clist
    for i in clist:
        for j in i:
            print "Next:", j, n
            n += 1
            if n >= 100: break
        if n >= 100: break
    print clist
    return clist

if __name__ == "__main__":
    main()
