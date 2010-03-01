class CircularList:
    """

    A CircularList will store up to maxSize items. A size of -1
    indicates that the list has no maxSize.  Use the addItem method to
    insert an item into the list.  It will automatically remove the
    oldest item in the list if it has reached the maxSize.  Use the
    nextItem method to retrieve the oldest visited item. Use the
    getItem method to retrieve an item at a particular index.
    
    """
    def __init__(self, size=-1):
        self.maxSize = size
        self.next = 0
        self.contents = []

    def __str__(self):
        output = ""
        if len(self.contents) == 0:
            return output + "Empty"
        output += "| "
        for i in range(len(self.contents)):
            if i == self.next:
                output += " ^ "
            output += (str(self.contents[i]) + " ")
        return output + " |"

    def __len__(self):
        return len(self.contents)

    def getItem(self, index):
        if index >= 0 and index < len(self.contents):
            return self.contents[index]
        raise AttributeError, "no item at index %d in CircularList" % index

    def addItem(self, item):
        if len(self.contents) == self.maxSize:
            self.contents.pop(0)
        self.contents.append(item)

    def nextItem(self):
        if len(self.contents) == 0:
            raise AttributeError, "no nextItem in empty CircularList"
        item = self.contents[self.next]
        self.next = (self.next + 1) % len(self.contents)
        return item

if __name__ == "__main__":
    print "-------------------------------------------------"
    print "TEST: try to get the next item from an empty list"
    emptyList = CircularList()
    print emptyList
    try:
        emptyList.nextItem()
    except:
        print "successfully caught the error"
    print "-------------------------------------------------"
    print "TEST: try to get a particular item from an empty list"
    try:
        emptyList.getItem(4)
    except:
        print "successfully caught the error"
    print "-------------------------------------------------"
    print "TEST: create a list with a maximum size of 5"
    clist = CircularList(5)
    for i in range(5):
        clist.addItem(i)
    print clist
    for i in range(len(clist)):
        print clist.nextItem()
        print clist
    for i in range(3):
        clist.addItem(i*10)
    print clist
    print "Getting item at index two: ", clist.getItem(2)
    print "-------------------------------------------------"
    print "TEST: create a list with no maximum size"
    clist = CircularList()
    for i in range(5):
        clist.addItem(i)
    print clist
    for i in range(len(clist)):
        print clist.nextItem()
        print clist
    for i in range(3):
        clist.addItem(i*10)
    print clist
    print "-------------------------------------------------"
    print "TEST: create a circular list of cicular lists"
    clist = CircularList()
    clist.addItem(CircularList(3))
    clist.getItem(0).addItem('a')
    clist.getItem(0).addItem('b')
    clist.addItem(CircularList(3))
    clist.getItem(1).addItem('c')
    clist.addItem(CircularList(3))
    clist.getItem(2).addItem('d')
    clist.getItem(2).addItem('e')
    clist.getItem(2).addItem('f')
    for i in range(12):
        print clist
        print clist.nextItem().nextItem()

    
