#!/usr/bin/env python
# Pyro configure.py script

"""
  --defaults       Use --prefix and default version
     --prefix=        Set the prefix; used only with --default
  --version=       Force default Python version to use
  --locates        Defaults are determined by the locate command

  If you want to make a Makefile.cfg with known paths:

  python configure.py --prefix=/usr/local --version=2.1 --defaults
"""

import sys
from posixpath import exists, isdir, isfile, islink
from posix import popen
import os

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision: 2563 $"

if "--version" in map(lambda s: s[0:9], sys.argv):
    for command in sys.argv:
        if command[0:9] == "--version":
            com, pyverSuggest = command.split("=", 2)
else:
    print "Checking for versions of Python..."
    versions = [("python", "")]
    for i in range(22, 41):
        pyver = "python%.1f" % (i / 10.0)
        pipe = popen("which %s 2> /dev/null" % pyver )
        which = pipe.readline().strip()
        if which == '':
            pass
        else:
            versions.append((pyver, pyver[-3:]))
    pyverSuggest = versions[-1][1]

prefix = "/usr"
if "--prefix" in map(lambda s: s[0:8], sys.argv):
    for command in sys.argv:
        if command[0:8] == "--prefix":
            com, prefix = command.split("=", 2)
    
if "--defaults" in sys.argv:
    useDefaults = 1
else:
    useDefaults = 0
if "--locates" in sys.argv:
    useLocates = 1
    useDefaults = 0
else:
    useLocates = 0


def file_exists(file_name, type = 'file'):
    if len(file_name) == 0:
        return 0
    else:
        if exists(file_name):
            if type == 'file' and isfile(file_name):
                return 1
            elif type == 'dir' and isdir(file_name):
                return 1
            else:
                if islink(file_name):
                    print "INFO: using '%s' which is a link" % file_name
                    return 1
                else:
                    return 0
        else:
            return 0

def ask_yn(title, list_of_options):
    print title
    retval = ''
    for directory, desc, default in list_of_options:
        if ask("Option:    Do you want to build " + desc + "? (y/n)", 
               default, 0) == "y":
            retval = retval + " " + directory
    return retval

def ask(question, default, filecheck = 1, type = 'file', locate = ''):
   done = 0
   print "-------------------------------------------------------------------"
   while not done:
      print question
      if (locate) and not useDefaults:
          print "Looking for '%s'..." % locate 
          pipe = popen("locate \"%s\" 2> /dev/null" % locate )
          new_default = pipe.readline()
          new_default = new_default.strip()
          if new_default:
              default = new_default
          pipe.close()
      print 'Default = [' + default + ']: ',
      if useDefaults or useLocates:
          retval = ""
      else:
          retval = raw_input()
      if retval == "":
         retval = default
      if retval == 'none':
         done = 1
      elif not filecheck:
         done = 1
      elif useDefaults or useLocates or file_exists(retval, type):
         done = 1
      else:
         print "WARNING: '%s' does not exist, or wrong type (file or dir)!" % retval
   if retval == 'none':
      return ''
   else:
       return retval

print """
---------------------------------------------------------------------
This is the configure.py script for installing Pyro, Python Robotics.
Pressing ENTER by itself will accept the default (shown in brackets).
---------------------------------------------------------------------
"""
text = """
# Pyro - Python Robotics Config Script

# What version of Python do you want to build Pyro for?
# Leave empty if your python binary is just "python"
PYTHON_VERSION=%s

# Where exactly is python?
PYTHON_BIN=%s

# Where is this version of Python's include files?
PYTHON_INCLUDE=-I%s

# Where are X11 files (such as X11 include directory)?
X11_DIR = %s

#where are the player includes? 
PLAYER_INCLUDE=-I%s

# What subdirs to include in the make process?
CONFIGDIRS = %s

"""

print """
Please answer the following questions either by supplying a complete
answer, or by pressing ENTER to accept the default. This uses the
'locate' command on systems (where available) to search for the best
possible answer. If there is no default, you should enter a valid
answer or 'none'.
"""

python_script_name = ask("1. Python version number?", pyverSuggest, 0)

python_include_files = ask("2. Where are Python's include files?",
                           ("%s/include/python" + python_script_name) % prefix,
                           type = "dir",
                           locate = "include/python" + python_script_name)

python_bin_path = ask("3. What is Python's binary? (enter path and name)",
                           ("%s/bin/python" + python_script_name) % prefix,
                      locate = "bin/python" + python_script_name)

x11_include_dir = ask("4. Where is the X11 include directory (need rgb.txt)?",
                      "/usr/share/X11",
                      type = "dir",
                      locate = "/usr/share/X11")
		      
player_include_dir = ask(" 5. Where is the player include directory (if one, or 'none')?",
                       "none",
		       type= "dir",
		       locate = "include/player-2")

included_packages = ask_yn("\n6. Options:", [
    ('camera/device vision/cvision', "Image Processing", "y"),
    ('camera/v4l', "Video for Linux \n(requires Image Processing)", 
     "y"),
    ('camera/v4l2', "Video for Linux2 \n(requires Image Processing)", 
     "y"),
    ('camera/bt848', "BT848 Video for old Pioneers \n(requires Image Processing)", 
     "n"),
    ('camera/fake', "Simulated vision from files \n(requires Image Processing)", 
     "y"),
    ('camera/blob', "Stage simulated vision \n(requires Image Processing and Player)", 
     "ny"[int(player_include_dir != "")]),
    ('camera/player', "Gazebo simulated vision \n(requires Image Processing and Player)", 
     "ny"[int(player_include_dir != "")]),
    ('camera/aibo', "Aibo vision \n(requires Image Processing)", "y"),
    ('camera/robocup', "Robocup simulated vision \n(requires Image Processing)", 
     "y"),
    ('camera/fourway', "Splits a camera view in 2 or 4 \n(requires combined camera image)", 
     "y"),
    ('camera/stereo', "Stereo Vision from two cameras \n(requires 2 cameras)", 
     "y"),
    ('brain/psom brain/psom/csom_src/som_pak-dev', "Self-organizing Map (SOM)", 
     "y"),
    ('tools/cluster', "Cluster Analysis Tool", "y"),
    ])

fp = open("Makefile.cfg", "w")
fp.write(text % (python_script_name, python_bin_path, python_include_files,
                 x11_include_dir, player_include_dir,  included_packages))
fp.close()

print """
Configuration is complete!

You just created Makefile.cfg. You can run this again, or edit
Makefile.cfg by hand if you need to.

Now you are ready to run 'make' (if you aren't already)
"""
