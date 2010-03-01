from os import environ
from pyrobot.system import file_exists
from pyrobot import pyrobotdir
import ConfigParser
import string

class Configuration:
    def __init__(self, file = None):
        self.data = {
            "robot":       {},
            "brain":       {},
            "simulator":   {},
            "pyrobot":        {}
            }
        if file != None and file != "None":
            self.load(file)

    def display(self):
        for sec in self.data.keys():
            print "[%s]" % sec
            for opt in self.data[sec].keys():
                print opt, "=", self.data[sec][opt]
            print

    def get(self, name, opt):
        try:
            return self.data[name][opt]
        except:
            return None

    def put(self, name, opt, value):
        if not self.data.has_key(name):
            self.data[name] = {}
        self.data[name][opt] = value

    def processFile(self, file, cp):
        print "Loading config '%s'..." % file
        cp.read(file)
        for sec in cp.sections():
            name = string.lower(sec)
            if not self.data.has_key(name):
                self.data[name] = {}
            for opt in cp.options(sec):
                self.data[name][string.lower(opt)] = string.strip(cp.get(sec, opt))

    def save(self, file="pyrobot.ini"):
        fp = open(file, "w")
        for section in self.data:
            if section == "config": continue # don't save config, that's what we're doing!
            print >> fp, "[%s]" % section
            for item in self.data[section]:
                print >> fp, "%s=%s" % (item, self.data[section][item])
            print >> fp
        fp.close()

    def load(self, file = None):
        cp = ConfigParser.ConfigParser()
        if file_exists( pyrobotdir() + "/.pyrobot"): 
            self.processFile( pyrobotdir() + "/.pyrobot", cp)
        if file_exists( pyrobotdir() + "/pyrobot.ini"): # $PYRO?
            self.processFile( pyrobotdir() + "/pyrobot.ini", cp)
        if file_exists( pyrobotdir() +
                        "/.pyrobot-" + environ['HOSTNAME']):
            # $PYRO-HOSTNAME?
            self.processFile( pyrobotdir() +
                              "/.pyrobot-" + environ['HOSTNAME'], cp)
        if file_exists( pyrobotdir() +
                        "/pyrobot-" + environ['HOSTNAME'] + ".ini"):
            # $PYRO-HOSTNAME?
            self.processFile( pyrobotdir() +
                              "/pyrobot-" + environ['HOSTNAME'] + ".ini", cp)
        if file_exists( environ['HOME'] + "/.pyrobot"): # home dir?
            self.processFile( environ['HOME'] + "/.pyrobot", cp)
        if file_exists( environ['HOME'] + "/pyrobot.ini"): # home dir?
            self.processFile( environ['HOME'] + "/pyrobot.ini", cp)
        if file_exists(".pyrobot"): # current dir?
            self.processFile( ".pyrobot", cp)
        if file_exists("pyrobot.ini"): # current dir?
            self.processFile( "pyrobot.ini", cp)
        if file and file_exists(file):
            self.processFile( file, cp)

if __name__ == "__main__":
    config = Configuration()
    config.load("some.ini")
    config.display()
