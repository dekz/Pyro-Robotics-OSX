"""
OptionMenu widget modified to allow dynamic menu reconfiguration
and setting of highlightthickness
"""
from Tkinter import OptionMenu
from Tkinter import _setit
import copy

class Picklist(OptionMenu):
    """
    unlike OptionMenu, our kwargs can include highlightthickness
    and can change menu items dynamically.
    """
    def __init__(self, master, variable, value, *values, **kwargs):
        #get a copy of kwargs before OptionMenu.__init__ munges them
        kwargsCopy=copy.copy(kwargs)
        if 'highlightthickness' in kwargs.keys():
            del(kwargs['highlightthickness'])
        OptionMenu.__init__(self, master, variable, value, *values, **kwargs)
        self.config(highlightthickness = kwargsCopy.get('highlightthickness'))
        self.variable = variable
        self.command = kwargs.get('command')
    
    def setMenu(self, valueList, value=None):
        """
        clear and reload the menu with a new set of options.
        valueList - list of new options
        value - initial value to set the optionmenu's menubutton to 
        """
        self['menu'].delete(0,'end')
        for item in valueList:
            self['menu'].add_command(label = item,
                                     command=_setit(self.variable, item, self.command))
        if value != None:
            self.variable.set(value)

    def add(self, item, select = 0):
        """
        add an item to the menu.
        item - new string
        select - should we highlight it?
        """
        self['menu'].add_command(label=item,
                                 command=_setit(self.variable,item, self.command))
        if select:
            self.variable.set(item)

if __name__ == "__main__":
    from Tkinter import *
    root = Tk()
    var = StringVar()
    menu = Picklist(root, var, "a", "b", "c")
    menu.pack()
    menu.add("x", 1)
    menu.add("y")
    menu.add("z", 1)
    menu.setMenu(["1", "2", "3"])
    menu.setMenu(["4", "5", "6"], "5")
