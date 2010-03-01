import Tkinter, string

def roundStr(item, places=3):
   """If item is a float, rounds to N places; otherwise just makes item a string."""
   values = []
   if type(item) == list:
      for v in item:
         if type(v) == float:
            values.append(('%%.%df'% places) % v)
         else:
            values.append(str(v))
      return '[%s]' % string.join(values, ", ")
   else:
      return str(item)

class StatusBar(Tkinter.Frame):
   def __init__(self, master):
      Tkinter.Frame.__init__(self, master)
      self.label = Tkinter.Label(self, bd=1, relief=Tkinter.SUNKEN, anchor=Tkinter.W)
      self.label.pack(fill=Tkinter.X)

   def set(self, format, *args):
      self.label.config(text=format % args)
      self.label.update_idletasks()

   def clear(self):
      self.label.config(text="")
      self.label.update_idletasks()


####
#	Class Dialog
#
#	Purpose
#	Base class for many dialog box classes.
####

class Dialog:

	def __init__(self, master):
		self.master = master
		self.top = Tkinter.Toplevel(self.master)
		self.top.title(self.__class__.__name__)
		self.top.minsize(1, 1)
		self.myWaitVar = `self.top` + 'EndDialogVar'

	def Show(self):
		self.SetupDialog()
		self.CenterDialog()
		self.top.deiconify()
		self.top.focus()

	def TerminateDialog(self, withValue):
                self.top.setvar(self.myWaitVar, withValue)
		self.top.withdraw()
		
	def DialogCleanup(self):
		self.top.destroy()
		self.master.focus()

	def SetupDialog(self): 
		pass

	def CenterDialog(self):
		self.top.withdraw()
		self.top.update_idletasks()
		w = self.top.winfo_screenwidth()
		h = self.top.winfo_screenheight()
		reqw = self.top.winfo_reqwidth()
		reqh = self.top.winfo_reqheight()
		centerx = `(w-reqw)/2`
		centery = `(h-reqh)/2 - 100`
		geomStr = "+" + centerx + "+" + centery
		self.top.geometry(geomStr)

####
#	Class ModalDialog
#
#	Purpose
#	Base class for many modal dialog box classes.
####

class ModalDialog(Dialog):

	def __init__(self, master):
		Dialog.__init__(self, master)

	def Show(self):
		import string
		self.SetupDialog()
		self.CenterDialog()
                if self.top.winfo_viewable():
                   self.top.grab_set()
		self.top.focus()
		self.top.deiconify()
		self.top.waitvar(self.myWaitVar)
                #print "waitvar =", self.top.getvar(self.myWaitVar), type(self.top.getvar(self.myWaitVar))
                result = self.top.getvar(self.myWaitVar)
                #print "result =", result, type(result)
                if type(result) == type(1):
                   return self.top.getvar(self.myWaitVar)
                else:
                   return string.atoi(self.top.getvar(self.myWaitVar))

####
#	Class AlertDialog
#
#	Purpose
#	-------
#
#	AlertDialog's are widgets that allow one to pop up warnings, one line
#	questions etc. They return a set of standard action numbers being :-
#	0 => Cancel was pressed
#	1 => Yes was pressed
#	2 => No was pressed
#
#	Standard Usage
#	--------------
#
#	F = AlertDialog(widget, message)
#	action = F.Show()
####

class AlertDialog(ModalDialog):

	def __init__(self, widget, msg):
		self.widget = widget
		self.msgString = msg
		Dialog.__init__(self, widget)

	def SetupDialog(self):
		import string
		upperFrame = Tkinter.Frame(self.top)
		upperFrame['relief'] = 'raised'
		upperFrame['bd']	 = 1
		upperFrame.pack({'expand':'yes', 'side':'top', 'fill':'both' })
		self.bitmap = Tkinter.Label(upperFrame)
		self.bitmap.pack({'side':'left'})
		msgList = string.splitfields(self.msgString, "\n")
		for i in range(len(msgList)):
			msgText = Tkinter.Label(upperFrame)
			msgText["text"]	  = msgList[i]
			msgText.pack({'expand':'yes', 'side':'top', 'anchor':'nw', 
				'fill':'x' })
		self.lowerFrame = Tkinter.Frame(self.top)
		self.lowerFrame['relief'] = 'raised'
		self.lowerFrame['bd']	 = 1
		self.lowerFrame.pack({'expand':'yes', 'side':'top', 'pady':'2', 
			'fill':'both' })

	def OkPressed(self):
		self.TerminateDialog(1)

	def CancelPressed(self):
		self.TerminateDialog(0)

	def NoPressed(self):
		self.TerminateDialog(2)

	def CreateButton(self, text, command):
		self.button = Tkinter.Button(self.lowerFrame)
		self.button["text"]	  = text
		self.button["command"]   = command
		self.button.pack({'expand':'yes', 'pady':'2', 'side':'left'})

	def CreateTextBox(self, text, width = 30, default = ""):
		frame = Tkinter.Frame(self.lowerFrame)
		frame.pack({'expand':'yes', 'side' :'top', 'pady' :'2', 
			'fill' :'x'})
		frame['relief'] = 'raised'
		frame['bd']	 = '2'
		label = Tkinter.Label(frame)
		label['text'] = text
		label.pack({'side':'left', 'expand':'no', 'anchor':'w',
                            'fill':'none'})
		textbox = Tkinter.Entry(frame, width=width, bg="white")
                textbox.insert(0, default)
		textbox.pack({'expand':'no', 'side':'right', 'fill':'x'})
                self.textbox[text] = textbox
                return textbox
####
#	Class ErrorDialog
#
#	Purpose
#	-------
#
#	To pop up an error message
####

class ErrorDialog(AlertDialog):

	def SetupDialog(self):
		AlertDialog.SetupDialog(self)
		self.bitmap['bitmap'] = 'error'
		self.CreateButton("OK", self.OkPressed)
                #self.CreatePickListBox("Something", lambda: "Click!")


####
#	Class WarningDialog
#
#	Purpose
#	-------
#
#	To pop up a warning message.
####

class WarningDialog(AlertDialog):

	def SetupDialog(self):
		AlertDialog.SetupDialog(self)
		self.bitmap['bitmap'] = 'warning'
		self.CreateButton("Yes", self.OkPressed)
		self.CreateButton("No", self.CancelPressed)

####
#	Class QuestionDialog
#
#	Purpose
#	-------
#
#	To pop up a simple question
####

class QuestionDialog(AlertDialog):

	def SetupDialog(self):
		AlertDialog.SetupDialog(self)
		self.bitmap['bitmap'] = 'question'
		self.CreateButton("Yes", self.OkPressed)
		self.CreateButton("No", self.NoPressed)
		self.CreateButton("Cancel", self.CancelPressed)


class AskDialog(AlertDialog):
   def __init__(self, root, title, qlist):
      AlertDialog.__init__(self, root, title)
      self.title = title
      self.qlist = qlist
      self.textbox = {}
      
   def SetupDialog(self):
      AlertDialog.SetupDialog(self)
      self.bitmap['bitmap'] = 'question'
      self.CreateButton("Ok", self.OkPressed)
      self.CreateButton("Cancel", self.CancelPressed)
      for (text, default) in self.qlist:
         self.CreateTextBox(text, width=30, default=default)

class Watcher(Tkinter.Toplevel):
   def __init__(self, root):
      Tkinter.Toplevel.__init__(self, root)
      self.winfo_toplevel().title("Pyrobot Expression Watcher")
      self.data = []
      self.winfo_toplevel().protocol('WM_DELETE_WINDOW',self.minimize)

   def minimize(self):
      self.withdraw()

   def unwatch(self, exp):
      i = 0
      for (oldExp, textbox) in self.data:
         if oldExp == exp:
            self.data.pop(i)
            textbox.destroy()
            return
         i += 1
      raise AttributeError, "expression not found: '%s'" % exp

   def watch(self, exp):
      self.deiconify()
      for (oldExp, textbox) in self.data:
         if oldExp == exp:
            return # don't watch the same expression more than once
      frame = self.CreateTextBox(exp, width=30, default="")
      self.data.append( (exp, frame))

   def update(self, locals = None):
      if locals == None:
         locals = globals()
      for exp, frame in self.data:
         try:
            value = roundStr(eval(exp, locals))
         except:
            value = "<Undefined>"
         frame.textbox.delete(0, 'end')
         frame.textbox.insert(0, value)

   def CreateTextBox(self, text, width = 30, default = ""):
      frame = Tkinter.Frame(self)
      frame.pack({'expand':'no', 'side' :'top', 'pady' :'2', 
                  'fill' :'x'})
      frame['relief'] = 'raised'
      frame['bd']	 = '2'
      label = Tkinter.Label(frame)
      label['text'] = text
      label.pack({'side':'left', 'expand':'no', 'anchor':'w',
                  'fill':'none'})
      textbox = Tkinter.Entry(frame, width=width, bg="white")
      textbox.insert(0, default)
      textbox.pack({'expand':'yes', 'side':'right', 'fill':'x'})
      label.bind("<1>", lambda event: self.unwatch(text))
      frame.textbox = textbox
      return frame

####
#	Class MessageDialog
#
#	Purpose
#	-------
#
#	To pop up a message.
####

class MessageDialog(AlertDialog):

	def SetupDialog(self):
		AlertDialog.SetupDialog(self)
		self.bitmap['bitmap'] = 'warning'
		self.CreateButton("Dismiss", self.CancelPressed)

####
#	Class FileDialog
#
#	Purpose
#	-------
#
#	FileDialog's are widgets that allow one to select file names by
#	clicking on file names, directory names, filters, etc.
#
#	Standard Usage
#	--------------
#
#	F = FileDialog(widget, some_title, some_filter)
#	if F.Show() != 1:
#		F.DialogCleanup()
#	return
#		file_name = F.GetFileName()
#		F.DialogCleanup()
####

class FileDialog(ModalDialog):

	#	constructor

	def __init__(self, widget, title, filter="*", pyro_dir = ''):
		from os import getcwd
		from string import strip

		self.widget = widget
		self.filter = strip(filter)
		self.orig_dir = getcwd()
                self.pyro_dir = pyro_dir
		self.cwd = getcwd()
                self.lastCwd = self.cwd
                self.defaultFilename =""
                #	the logical current working directory
		Dialog.__init__(self, widget)

	#	setup routine called back from Dialog

        def HomePressed(self):
           from os import getenv
           if self.goHomeButton['text'] == 'Home':
              #if self.cwd != getenv('HOME') and \
              #       self.cwd != self.pyro_dir:
              self.lastCwd = self.cwd
              self.cwd = getenv('HOME')
              self.goHomeButton['text'] = 'Pyrobot'
              self.UpdateListBoxes()
           elif self.goHomeButton['text'] == 'Last':
              tmp = self.cwd 
              self.cwd = self.lastCwd
              #if tmp != getenv('HOME') and \
              #       tmp != self.pyro_dir:
              self.lastCwd = tmp
              self.goHomeButton['text'] = 'Home'
              self.UpdateListBoxes()
           elif self.goHomeButton['text'] == 'Pyrobot':
              #if self.lastCwd != getenv('HOME') and \
              #       self.lastCwd != self.pyro_dir:
              #   self.goHomeButton['text'] = 'Last'
              #else:
              self.goHomeButton['text'] = 'Home'
              self.lastCwd = self.cwd
              self.cwd = self.pyro_dir
              self.UpdateListBoxes()

	def SetupDialog(self):

		# directory label

		self.dirFrame = Tkinter.Frame(self.top)
		self.dirFrame['relief'] = 'raised'
		self.dirFrame['bd']	 = '2'
		self.dirFrame.pack({'expand':'no', 'side':'top', 'fill':'both'})
		self.dirLabel = Tkinter.Label(self.dirFrame)
		self.dirLabel["text"] = "Directory:"
		self.dirLabel.pack({'expand':'no', 'side':'left', 'fill':'none'})
		# editable filter

		self.filterFrame = Tkinter.Frame(self.top)
		self.filterFrame['relief'] = 'raised'
		self.filterFrame['bd']	 = '2'
		self.filterFrame.pack({'expand':'no', 'side':'top', 'fill':'both'})
		self.filterLabel = Tkinter.Label(self.filterFrame)
		self.filterLabel["text"] = "Filter:"
		self.filterLabel.pack({'expand':'no', 'side':'left', 'fill':'none'})
                self.goHomeButton = Tkinter.Button(self.filterFrame)
		self.goHomeButton["text"]	  = "Home"
		self.goHomeButton["command"]   = self.HomePressed
		self.goHomeButton["width"] = 8
		self.goHomeButton.pack({'expand':'yes', 'pady':'2', 'side':'right'})
                
		self.filterEntry = Tkinter.Entry(self.filterFrame)
		self.filterEntry.bind('<Return>', self.FilterReturnKey)
		self.filterEntry["width"]  = "40"
		self.filterEntry["relief"] = "ridge"
		self.filterEntry.pack({'expand':'yes', 'side':'right', 'fill':'x'})
		self.filterEntry.insert(0, self.filter)

		# the directory and file listboxes

		self.listBoxFrame = Tkinter.Frame(self.top)
		self.listBoxFrame['relief'] = 'raised'
		self.listBoxFrame['bd']	 = '2'
		self.listBoxFrame.pack({'expand':'no', 'side' :'top',
			'pady' :'2', 'padx': '0', 'fill' :'x'})
		self.CreateDirListBox()
		self.CreateFileListBox()
		self.UpdateListBoxes()

		# editable filename

		self.fileNameFrame = Tkinter.Frame(self.top)
		self.fileNameFrame.pack({'expand':'no', 'side':'top', 'fill':'both'})
		self.fileNameFrame['relief'] = 'raised'
		self.fileNameFrame['bd']	 = '2'
		self.fileNameLabel = Tkinter.Label(self.fileNameFrame)
		self.fileNameLabel["text"] = "File:"
		self.fileNameLabel.pack({'expand':'no', 'side':'left', 'fill':'none'})
		self.fileNameEntry = Tkinter.Entry(self.fileNameFrame)
		self.fileNameEntry["width"]  = "40"
		self.fileNameEntry["relief"] = "ridge"
		self.fileNameEntry.pack({'expand':'yes', 'side':'right', 'fill':'x'})
		self.fileNameEntry.bind('<Return>', self.FileNameReturnKey)
                if self.defaultFilename:
                   self.fileNameEntry.insert(0, self.defaultFilename)

                # help text:
                helpFrame = Tkinter.Frame(self.top)
                scrollBar = Tkinter.Scrollbar(helpFrame, {'orient':'vertical'})
                scrollBar.pack({'expand':'no', 'side':'right', 'fill':'y'})
                self.helpText = Tkinter.Text(helpFrame, state="disabled",
                                             yscroll = scrollBar.set,
                                             height = 5, width = 50)
                self.helpText.pack({'expand':'yes', 'side' :'top', 
                                    'pady' :'1','fill' :'both'})
                helpFrame.pack({'side':'top', 'expand':'yes', 'fill':'both'})
                scrollBar['command'] = self.helpText.yview

		#	buttons - ok, filter, cancel

		self.buttonFrame = Tkinter.Frame(self.top)
		self.buttonFrame['relief'] = 'raised'
		self.buttonFrame['bd']	 = '2'
		self.buttonFrame.pack({'expand':'no', 'side':'top', 'fill':'x'})
		self.okButton = Tkinter.Button(self.buttonFrame)
		self.okButton["text"]	  = "OK"
		self.okButton["command"]   = self.OkPressed
		self.okButton["width"] = 8
		self.okButton.pack({'expand':'yes', 'pady':'2', 'side':'left'})
		self.filterButton = Tkinter.Button(self.buttonFrame)
		self.filterButton["text"]	  = "Filter"
		self.filterButton["command"]   = self.FilterPressed
		self.filterButton["width"] = 8
		self.filterButton.pack({'expand':'yes', 'pady':'2', 'side':'left'})
		button = Tkinter.Button(self.buttonFrame)
		button["text"] = "Cancel"
		button["command"] = self.CancelPressed
		button["width"] = 8
		button.pack({'expand':'yes', 'pady':'2', 'side':'left'})

		button = Tkinter.Button(self.buttonFrame)
		button["text"] = "Edit"
		button["command"] = self.EditPressed
		button["width"] = 8
		button.pack({'expand':'yes', 'pady':'2', 'side':'left'})

		button = Tkinter.Button(self.buttonFrame)
		button["text"] = "My Copy"
		button["command"] = self.CopyPressed
		button["width"] = 8
		button.pack({'expand':'yes', 'pady':'2', 'side':'left'})

	#	create the directory list box

	def CreateDirListBox(self):
		frame = Tkinter.Frame(self.listBoxFrame)
		frame.pack({'expand':'yes', 'side' :'left', 'pady' :'1', 
			'fill' :'both'})
		frame['relief'] = 'raised'
		frame['bd']	 = '2'
		filesFrame = Tkinter.Frame(frame)
		filesFrame['relief'] = 'flat'
		filesFrame['bd']	 = '2'
		filesFrame.pack({'side':'top', 'expand':'no', 'fill':'x'})
		label = Tkinter.Label(filesFrame)
		label['text'] = 'Directories:'
		label.pack({'side':'left', 'expand':'yes', 'anchor':'w',
			'fill':'none'})
		scrollBar = Tkinter.Scrollbar(frame, {'orient':'vertical'})
		scrollBar.pack({'expand':'no', 'side':'right', 'fill':'y'})
		self.dirLb = Tkinter.Listbox(frame, {'yscroll':scrollBar.set})
		self.dirLb.pack({'expand':'yes', 'side' :'top', 'pady' :'1', 
			'fill' :'both'})
		self.dirLb.bind('<Double-Button-1>', self.DoDoubleClickDir)
		scrollBar['command'] = self.dirLb.yview

	#	create the files list box

	def CreateFileListBox(self):
		frame = Tkinter.Frame(self.listBoxFrame)
		frame['relief'] = 'raised'
		frame['bd']	 = '2'
		frame.pack({'expand':'yes', 'side' :'left', 'pady' :'1', 'padx' :'1', 
			'fill' :'both'})
		filesFrame = Tkinter.Frame(frame)
		filesFrame['relief'] = 'flat'
		filesFrame['bd']	 = '2'
		filesFrame.pack({'side':'top', 'expand':'no', 'fill':'x'})
		label = Tkinter.Label(filesFrame)
		label['text'] = 'Files:'
		label.pack({'side':'left', 'expand':'yes', 'anchor':'w', 
			'fill':'none'})
		scrollBar = Tkinter.Scrollbar(frame, {'orient':'vertical'})
		scrollBar.pack({'side':'right', 'fill':'y'})
		self.fileLb = Tkinter.Listbox(frame, {'yscroll':scrollBar.set})
		self.fileLb.pack({'expand':'yes', 'side' :'top', 'pady' :'0', 
			'fill' :'both'})
		self.fileLb.bind('<1>', self.DoSelection)
                # This causes some problems on Debian computers
		self.fileLb.bind('<Double-Button-1>', self.DoDoubleClickFile)
		scrollBar['command'] = self.fileLb.yview

	#	update the listboxes and directory label after a change of directory

	def UpdateListBoxes(self):
		import os
		from commands import getoutput
		from string import splitfields

		cwd = self.cwd
		self.fileLb.delete(0, self.fileLb.size())
		filter = self.filterEntry.get()
		# '*' will list recurively, we don't want that.
		if filter == '*':
			filter = ''
                if os.name in ['nt', 'dos', 'os2'] :
                   cmd = "dir /b \"" + os.path.join(cwd, filter) + "\""
                   pipe = os.popen(cmd + ' 2>&1', 'r')
                   cmdOutput = pipe.read()
                   pipe.close()
                elif os.name in ['posix']:
                   cmd = "ls " + os.path.join(cwd, filter) + \
                         " | grep -v __init__.py"
                   cmdOutput = getoutput(cmd)
                else:
                   raise AttributeError, "your OS (%s) is not supported" % os.name
		files = splitfields(cmdOutput, "\n")
                files.sort()
		for i in range(len(files)):
			if os.path.isfile(os.path.join(cwd, files[i])):
				self.fileLb.insert('end', os.path.basename(files[i]))
		files = os.listdir(cwd)
                if cwd != '/':
                   files.append('..')
		files.sort()
		self.dirLb.delete(0, self.dirLb.size())
		for i in range(len(files)):
                   if os.path.isdir(os.path.join(cwd, files[i])):
                      if files[i] != 'CVS' and (files[i][0] != '.' or files[i] == '..'):
                         self.dirLb.insert('end', files[i])
		self.dirLabel['text'] = "Directory:" + self.cwd_print()

	#	selection handlers

	def DoSelection(self, event):
		from posixpath import join
                import string
		lb = event.widget
		field = self.fileNameEntry
		field.delete(0, Tkinter.AtEnd())
		field.insert(0, join(self.cwd_print(), lb.get(lb.nearest(event.y))))
                lb.select_clear(0, "end")
                lb.select_anchor(lb.nearest(event.y))
                # ------------------------------------
                # Get some help from the file
                # this could be the __docs__ string from
                # the module, but that would require us to load it
                # and that seems like not a good idea. Maybe better
                # to get data from a text file, or top of .py file
                if field.get()[-3:] == ".py" or field.get()[-6:] == ".world":
                   fp = open(field.get(), "r")
                   lines = fp.readlines()
                   stringlines = string.join(lines, '')
                   fp.close()
                else:
                   stringlines = "Click the 'OK' button to load."
                self.helpText.config(state='normal')
                self.helpText.delete(1.0, 'end')
                self.helpText.insert('end', stringlines )
                self.helpText.config(state='disabled')

	def DoDoubleClickDir(self, event):
		from posixpath import join
		lb = event.widget
		self.cwd = join(self.cwd, lb.get(lb.nearest(event.y)))
		self.UpdateListBoxes()

	def DoDoubleClickFile(self, event):
		self.OkPressed()

	def OkPressed(self):
		self.TerminateDialog(1)

	def FileNameReturnKey(self, event):
		from posixpath import isabs, expanduser, join
		from string import strip
		#	if its a relative path then include the cwd in the name
		name = strip(self.fileNameEntry.get())
		if not isabs(expanduser(name)):
			self.fileNameEntry.delete(0, 'end')
			self.fileNameEntry.insert(0, join(self.cwd_print(), name))
		self.okButton.flash()
		self.OkPressed()
	
	def FilterReturnKey(self, event):
		from string import strip
		filter = strip(self.filterEntry.get())
		self.filterEntry.delete(0, 'end')
		self.filterEntry.insert(0, filter)
		self.filterButton.flash()
		self.UpdateListBoxes()

	def FilterPressed(self):
		self.UpdateListBoxes()

	def CancelPressed(self):
		self.TerminateDialog(0)

        def CopyPressed(self):
           import os
           filename = self.fileNameEntry.get()
           myfilename = os.getenv("HOME") + "/my" + filename.split("/")[-1]
           if os.name in ['nt', 'dos', 'os2'] :
              os.system("copy %s %s" %(filename, myfilename))              
           else:
              os.system("cp -i %s %s" %(filename, myfilename))
           self.fileNameEntry.delete(0, 'end')
           self.fileNameEntry.insert(0, myfilename)
           self.EditPressed(myfilename, 1)

        def EditPressed(self, filename = None, selectIt = 0):
           import os
           if filename == None:
              filename = self.fileNameEntry.get()
           if os.getenv("EDITOR"): 
              editor = os.getenv("EDITOR")
           else:
              editor = "emacs"
           os.system("%s %s &" % (editor, filename))
           self.TerminateDialog(0) #selectIt)

	def GetFileName(self):
		return self.fileNameEntry.get()
		
	#	return the logical current working directory in a printable form
	#	ie. without all the X/.. pairs. The easiest way to do this is to
	#	chdir to cwd and get the path there.

	def cwd_print(self):
		from os import chdir, getcwd
		chdir(self.cwd)
		p = getcwd()
		chdir(self.orig_dir)
		return p

####
#	Class LoadFileDialog
#
#	Purpose
#	-------
#
#	Specialisation of FileDialog for loading files.
####

class LoadFileDialog(FileDialog):

        def __init__(self, master, title, filter, pyro_dir = ''):
           FileDialog.__init__(self, master, title, filter, pyro_dir)
           self.top.title(title)

	def OkPressed(self):
		fileName = self.GetFileName()
		if file_exists(fileName) == 0:
			str = 'File ' + fileName + ' not found.'
			errorDlg = ErrorDialog(self.top, str)
			errorDlg.Show()
			errorDlg.DialogCleanup()
			return
		FileDialog.OkPressed(self)

####
#	Class SaveFileDialog
#
#	Purpose
#	-------
#
#	Specialisation of FileDialog for saving files.
####

class SaveFileDialog(FileDialog):
        def __init__(self, master, title, filter, defaultFilename=""):
                FileDialog.__init__(self, master, title, filter)
                self.defaultFilename = defaultFilename
		self.top.title(title)

	def OkPressed(self):
		fileName = self.GetFileName()
		if file_exists(fileName) == 1:
			str = 'File ' + fileName + ' exists.\nDo you wish to overwrite it?'
			warningDlg = WarningDialog(self.top, str)
			if warningDlg.Show() == 0:
				warningDlg.DialogCleanup()
				return
			warningDlg.DialogCleanup()
		FileDialog.OkPressed(self)

class Application(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)


        self.button = Tkinter.Button(self)
        self.button['text'] = 'Load File...'
        self.button['command'] = self.Press
        self.button.pack({"side": "top"})

        self.pack()

    def Press(self):
        fileDlg = filedlg.LoadFileDialog(app, "Load File", "*", '')
        if fileDlg.Show() != 1:
            fileDlg.DialogCleanup()
            return
        fname = fileDlg.GetFileName()
        self.button['text'] = 'File: ' + fname
        fileDlg.DialogCleanup()

#
#	Return whether a file exists or not.
#	The file "" is deemed to not exist
#

def file_exists(file_name):
	from posixpath import exists
	import string
	if len(file_name) == 0:
		return 0
	else:
		return exists(file_name)

#
#	read the lines from a file and strip them of their trailing newlines
#

def readlines(fd):
	from string import strip
	return map(lambda s, f=strip: f(s), fd.readlines())

#
#	Various set operations on sequence arguments.
#	in joins the values in 'a' take precedence over those in 'b'
#

def seq_join(a, b):
	res = a[:]
	for x in b:
		if x not in res:
			res.append(x)
	return res

def seq_meet(a, b):
	res = []
	for x in a:
		if x in b:
			res.append(x)
	return res

def seq_diff(a, b):
	res = []
	for x in a:
		if x not in b:
			res.append(x)
	return res

#
#	Various set operations on map arguments.
#	The values in 'a' take precedence over those in 'b' in all cases.
#

def map_join(a, b):
	res = {}
	for x in a.keys():
		res[x] = a[x]
	for x in b.keys():
		if not res.has_key(x):
			res[x] = b[x]
	return res

def map_meet(a, b):
	res = {}
	for x in a.keys():
		if b.has_key(x):
			res[x] = a[x]
	return res

def map_diff(a, b):
	res = {}
	for x in a.keys():
		if not b.has_key(x):
			res[x] = a[x]
	return res

#
#	Join a map of defaults values with a map of set values. The defaults 
#	map is taken to be total, and hence any keys not in the defaults, but 
#	in the settings, must be errors.
#

def map_join_total(settings, defaults):
	res = map_join(settings, defaults)
	for x in settings.keys():
		if not defaults.has_key(x):
			raise "merge_defaults"
	return res

#
#	Return a string being the concatenation of a sequence of objects
#	NOTE: we apply the routine recursively to sequences of sequences
#

def seq_to_str(s):
	if type(s) == type((1,)) or type(s) == type([]):
		return reduce(lambda sum, a: sum + seq_to_str(a), s, "")
	else:
		return str(s)

#
#	a dummy function for any number of arguments
#

def dummy(*args):
	pass

#
#	the true and false functions for any number of args
#

def true(*args):
	return 1

def false(*args):
	return 0

#
#	return whether a char is printable or not
#

def is_printable(c):
	o = ord(c)
	return c == "\n" or (o >= 32 and o <= 126)

#
#	return a printable version of a given string
#	by simply omitting non printable characters
#

def string_printable(s):
	length = len(s)
	ok = 1
	res = ""
	l = 0
	for i in range(length):
		if not is_printable(s[i]):
			res = res + s[l:i]
			l = i+1
			ok = 0
	if ok:
		return s
	else:
		return res + s[l:length]


if __name__ == "__main__":
   from Tkinter import Tk
   tk = Tk()
   w = Watcher(tk)
   w.watch("w")
   w.mainloop()
