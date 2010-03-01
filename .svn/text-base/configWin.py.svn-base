import compileall, os

__author__ = "Douglas Blank <dblank@brynmawr.edu>"
__version__ = "$Revision$"

versionString = """def version():
    return "5.0.0"
"""

fp = open("system/version.py", "w")
fp.write(versionString)
fp.close()

os.system('copy build\pyrobot bin\pyrobot.pyw')

compileall.compile_dir(".")
