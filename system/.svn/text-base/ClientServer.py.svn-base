#
#	All communication between Client and Server are done through
#		Message objects. NO REGULAR TEXT EXCHANGE!
#
#	Protocol: Server will return a message for every message it gets!
#


from pyrobot.gui import console
import socket
import SocketServer
import cPickle
import sys
import os
import time
import thread

PYROPORT = 1408
MSG_MAX_LEN = 10000

class Server(SocketServer.TCPServer):
	def __init__(self, ip_port, handler):
		"""
		The official - behind the scenes - init
		don't change anything
		add any init code to init_world()
		this init will reserve IP_Port and stuff like that
		"""
		self.alive = 1
		self.request_queue_size = 10
		shift = 0		
		while 1:
			try:
				console.log(console.INFO,'Trying port :' + str(PYROPORT+shift))
				#print "trying port:",PYROPORT+shift
				SocketServer.TCPServer.__init__(self,ip_port, \
								handler)
				break
			except:
				shift += 1
				ip_port=("localhost",PYROPORT+shift)
				if (shift > 10):
					break
			
		if (shift>10):
			console.log(console.FATAL,'Can\'t bind ' + str(ip_port))
			return
		else:
			console.log(console.INFO,'Server at ' + str(ip_port))
		self.init_world()

	def init_world(self):
		pass
		
	def serve(self):
		self.serve_forever()
	
		
	def quit(self):
		console.log(console.INFO,'Server is quitting')
		#self.socket.shutdown(0)
		self.alive = 0
		self.socket.close()
	

#	def serve_forever(self):
#		console.log(console.INFO,'Server is running forever')
#		SocketServer.TCPServer.serve_forever(self)
		
	#override serv_forever
	def serv_forever(self):
		while self.alive == 1:
			self.handle_request() # tcp/socket call

	def process_request(self, request, client_address):
		"""
		We override this funciton to allow multi-threaded server-request processing
		i.e. allow multiple connections
		"""
		thread.start_new_thread(self.finish_request, (request, client_address))

"""class MyServerQuit:
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return `self.value`"""


class Client:
	"""
	Client Class
	"""
	def __init__(self, host="localhost", port=PYROPORT):
		"""
		Init the class - define socket type
		"""
		self.host = host
		self.port = port
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		console.log(console.INFO,'Client init')
		self.alive = 1	#0 for false, 1 for true - flag to quit
		
	def connect(self):
		"""
		Connect to server - already defined in init
		"""
		shift = 0
		done = 0
		while not done:
			try:
				console.log(console.INFO,"trying port:" + str(self.port+shift))
				self.s.connect((self.host, self.port+shift))
				self.port += shift
				self.init_server()
				break
			except:
				console.log(console.WARNING, "Connection failed" + str(sys.exc_info()[0]))
				#print "eer=",sys.exc_info()[0],']'
				#for some reason, I need to restart the socket
				#after every failed try to connect
				self.s.close()
				self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				shift += 1
				if (shift > 10):
					break
					
		if (shift>10):
			console.log(console.FATAL,'Client can\'t connect:' + `self.host + ":"\
				+ str(self.port)`)
			self.alive = 0
		else:				
			console.log(console.INFO,'Client connected to ' + `self.host + ":"\
				+ str(self.port)`)
	
	def init_server(self):
		"""
		This function will send a verification message to test if
		client is connected to a SimServer or some other one!
		It will raise an exception if it was wrong
		"""
		self.send(Message("Init"))
		ret = self.receive()
		if (ret.type == "OK" and ret.body=="Init"):#Good server!
			console.log(console.INFO,'Server Verified')
		else:
			console.log(console.INFO,'Server incompatible')
			raise ConnectionError, 'Wrong Server'
			
	
	def send(self, smsg):#smsg - Message
		"""
		Pickles a Message obj, and sends it
		"""
		#pickle it
		data = cPickle.dumps(smsg,0)#0 means ASCII encryption
		#send the resulting string
		self.sendString(data)
	
	def receive(self):
		"""
		Rewceives a string, unpickle it, then returns the Message object
		"""
		#get msg
		msg = self.receiveString()
		#smsg = Message()
		try:
			#unpickle it
			smsg = cPickle.loads(msg)
		except:
			#error
			console.log(console.ERROR,'Unrecognized msg format[' + msg+']')
			#raise
			#print "error=[", sys.exc_info()[0],"]"
			smsg = Message()			
		return smsg
	
	
	def sendString(self, message):
		"""
		sends message to open socket
		"""
		#print "Send:\t", message
		self.s.send(message)
		
	def receiveString(self):
		"""receive from server"""
		return self.s.recv(MSG_MAX_LEN)
		
	def listenString(self,times=-1):
		""" unlimited receive """
		while times != 0:
			times = times - 1
			msg = self.receiveString()
			#print "Recv:\t", msg
			#if (msg != None):
			#print "Received:" + str(times) + ":[" + msg + "]"
			
	def terminal(self):
		"""will send user command, then listen to server once"""
		self.usersend()
		while self.alive:
			self.listenString(1)
			self.usersend()
	
	def usersend(self):
		"""will send whatever the user types - every line"""
		print "Enter commands for server:"
		msg = sys.stdin.readline()
		if (msg == "exit\012"):
			self.alive=1
		else:
			self.sendString(msg)		
	
	def disconnect(self):
		""" just call self.close() """
		self.close()
	
	def close(self):
		""" Close connection """
		console.log(console.INFO,'Client closing')
		self.s.close()

class Message:
	"""
	This class will be the main block of communication
	between server/client
	Possible types:
	
	1- RawCode: Raw code to run
		type: 'ExecCode'
		body: String containing all commands to be executed
		agrs: none
	2- type: 'OK' confirmation of something body: 'the something'
	3- type: 'Error', body: 'Error message'
		

	"""
	def __init__(self, type="None", body="", args={}):
		self.type = type
		self.body = body
		self.args = args
	
	def toString(self):
		res = "[" + self.type + "," + self.body + "," + str(self.args) + "]"
		return res

class ReqHandler(SocketServer.BaseRequestHandler):
	def handle(self):	
		console.log(console.INFO,'Connection Request')
		#print "req:",self.request,"ser:",self.server,"client:",self.client_address
		#print "socket=" , self.request.socket
		self.done = 0
		while not self.done:
			data = self.request.recv(MSG_MAX_LEN)
			if not data: break #client forced close connection
			
			try:
				#unpickle the message
				msg = cPickle.loads(data)
			except:
				#error
				console.log(console.ERROR,'Unrecognized msg format[' + data+']')
				sendmsg = Message(type="String",body="Error - no format")
			else:			
				sendmsg = self.process(msg)
			#there must be a response for each incoming message

			#pickle the message out
			senddata = cPickle.dumps(sendmsg,0)#0 for ASCII encrypt
			#print "Send:\t",`senddata`
			self.request.send(senddata)
			
		#close connection
		self.request.close()

	def process(self,data):
		"""this functin will handle all the incoming messages from client
		args: data - Message class
		return: msg - Message class
		"""
		if (data.type == "Init"):
			msg = Message("OK","Init")
		elif (data.type == "ExecCode"):
			#run code
			exec data.body
			msg = Message("OK","ExecCode")
		elif (data.type == "Robot"):
			#any messages that deal with robots
			msg = self.process_robot(data)
		else:
			console.log(console.WARNING,'Unknown message type from client['\
			 + data.type + ']')
			msg = Message("Error","unknown type[" + data.type + "]")		
		return msg
		
	def process_robot(self, data):
		pass



if (__name__ == '__main__'):
	print 'Testing SimServer & SimClient'
	process = os.fork()
	if process:
		ss = Server()
		ss.serve_forever()	#listen infinitely

	sc = Client()
	sc.connect()
	if (sc.alive):
		print 'press enter to test exec'
		sys.stdin.readline()
		sc.send(Message("ExecCode","print 'testing success'"))
		ret = sc.receive()
		print ret.toString()
		print 'press enter to move on'
		sys.stdin.readline()
		sc.send(Message("wrong","testing error"))
		ret = sc.receive()
		print ret.toString()
		print 'press enter to finish'
		sys.stdin.readline()
		sc.close()
	