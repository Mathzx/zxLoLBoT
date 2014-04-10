#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
An easy to use framework for writing league of legends chat bots using the xmpp protocol.
You can create commands by decorating functions.
"""

import sys
import json
import inspect
import threading
import urllib.error
import urllib.parse
import urllib.request

try:
	import sleekxmpp
except ImportError:
	print("You need to install sleekxmpp from http://sleekxmpp.com")
	sys.exit(-1)
try:
	import dns
except ImportError:
	print("You need to install dnspython from http://www.dnspython.org")
	sys.exit(-1)

def botcommand(*args, **kwargs):
	"""Decorator for bot command function"""

	def decorate(function, hidden=False, admin=False, name=None):
		setattr(function, "__zxLoLBoT_command", True)
		setattr(function, "__zxLoLBoT_command_name", name or function.__name__)
		setattr(function, "__zxLoLBoT_command_admin", admin)
		setattr(function, "__zxLoLBoT_command_hidden", hidden)
		return function

	if len(args):
		return decorate(args[0], **kwargs)
	else:
		return lambda function: decorate(function, **kwargs)

class zxLoLBoT():
	def __init__(self, username, password, region="NA"):
		"""Initializes the bot and sets up commands."""

		#XMPP
		self.xmpp			= sleekxmpp.ClientXMPP(username+"@pvp.net/xiff", "AIR_"+password)

		#Server
		self.servers 		= {"NA" : "chat.na1.lol.riotgames.com", "EUW": "chat.eu.lol.riotgames.com", "EUNE": "chat.eun1.lol.riotgames.com"} #NA: North America, EUW: EU West, EUNE: EU Nordic/East
		self.port 			= 5223
		
		#Account
		self.username		= username
		self.password		= password
		self.riotApiKey		= None
		self.region 		= region
		self.recentlyAdded	= []
		self.friendsOnline	= [] #TODO: more than likely something to do with this
		self.status			= {}
		self.admins			= []

		#XMPP Events
		self.xmpp.add_event_handler("presence_unsubscribe", self.onXMPPPresenceUnsubscribe)
		self.xmpp.add_event_handler("presence_subscribe", self.onXMPPPresenceSubscribe)
		self.xmpp.add_event_handler("failed_auth", self.onXMPPFailedAuth)
		self.xmpp.add_event_handler("got_offline", self.onXMPPGotOffline)
		self.xmpp.add_event_handler("got_online", self.onXMPPGotOnline)
		self.xmpp.add_event_handler("session_start", self.onXMPPStart)
		self.xmpp.add_event_handler("disconnected", self.onXMPPDisconnected)
		self.xmpp.add_event_handler("message", self.onXMPPMessage)

		#Commands
		self.helpCommand 	= True
		self.commands 		= {}

		#Misc
		self.summonerIdsToName = {}

		#Custom messages
		self.notAdminMessage 		= None
		self.someoneAddedMessage 	= "Thank you for adding me.\nType help to start"
		self.someoneOnlineMessage 	= None
		self.invalidCommandMessage 	= None

		#Testing region and setting up commands registered via the decorator botcommand
		if region not in self.servers.keys():
			print("Invalid region. Please use any of the regions below:\nNA\tNorth america\nEUW\tEU West\nEUNE\tEU Nordic/East")
			sys.exit(-1)
		for name, value in inspect.getmembers(self):
			if inspect.ismethod(value) and getattr(value, "__zxLoLBoT_command", False):
				name = getattr(value, "__zxLoLBoT_command_name")
				self.commands[name] = value
				print("Registered bot command: " + name)

	def onXMPPPresenceSubscribe(self, presence):
		"""Handler for XMPP presence subscribes"""
		self.recentlyAdded.append(str(presence["from"])+"/xiff")
		summonerId = self.jidToSummonerId(presence["from"])
		if self.riotApiKey:
			if summonerId not in self.summonerIdsToName:
				self.summonerIdsToName[summonerId] = self.summonerIdToName(summonerId)
			self.fireEvent("someoneAdded", who=self.summonerIdsToName[summonerId])
			print(self.summonerIdsToName[summonerId] + " just added you")
		else:
			self.fireEvent("someoneAdded", who=str(presence["from"]))
			print(str(presence["from"]) + " just added you")

	def onXMPPPresenceUnsubscribe(self, presence):
		"""Handler for XMPP presence unsubscribes"""

		if self.riotApiKey:
			if summonerId not in self.summonerIdsToName:
				self.summonerIdsToName[summonerId] = self.summonerIdToName(summonerId)
			self.fireEvent("someoneRemoved", who=self.summonerIdsToName[summonerId])
			print(self.summonerIdsToName[summonerId] + " just removed you")
		else:
			print(str(presence["from"]) + " just removed you")
			self.fireEvent("someoneRemoved", who=str(presence["from"]))

	def onXMPPStart(self, e):
		"""Handler for XMPP session start event"""

		self.xmpp.get_roster()
		self.xmpp.send_presence(ptype="chat", pstatus=self.getStatus())
		print("Successfully logged in")
		self.fireEvent("gotOnline")

	def onXMPPDisconnected(self, e):
		"""Handler for XMPP disconnected event"""

		self.fireEvent("gotOffline")

	def onXMPPGotOnline(self, presence):
		"""Handler for XMPP got online event"""

		if presence["from"] != self.xmpp.boundjid:
			self.friendsOnline.append(str(presence["from"]))
			self.xmpp.send_presence(pto=presence["from"], ptype="chat", pstatus=self.getStatus())
			self.fireEvent("someoneOnline", who=str(presence["from"]))
			if presence["from"] in self.recentlyAdded:
				self.recentlyAdded.remove(presence["from"])
				self.message(presence["from"], self.someoneAddedMessage) #TODO: make this optional, configure it somehow
				self.fireEvent("someoneAddedOnline", who=str(presence["from"]))
			else: #Avoids sending a message from someone recently addded and someone logging on at the same time
				if self.someoneOnlineMessage:
					self.message(presence["from"], self.someoneOnlineMessage)

	def onXMPPGotOffline(self, presence):
		"""Handler for XMPP got offline event"""

		if str(presence["from"]) in self.friendsOnline:
			self.friendsOnline.remove(str(presence["from"]))
			self.fireEvent("someoneOffline", who=str(presence["from"]))

	def onXMPPMessage(self, message):
		"""Handler for XMPP incoming messages event"""

		if message["type"] in ("chat", "normal"):
			#Event handling
			summonerId = self.jidToSummonerId(message["from"])
			if self.riotApiKey:
				if summonerId not in self.summonerIdsToName:
					self.summonerIdsToName[summonerId] = self.summonerIdToName(summonerId)
				self.fireEvent("message", sender=str(message["from"]), message=message["body"], summonerId=str(summonerId), summonerName=self.summonerIdsToName[summonerId])
			else:
				self.fireEvent("message", sender=str(message["from"]), message=message["body"], summonerId=str(summonerId))

			#Command handling
			command 	= message["body"].split()[0]
			arg 		= message["body"][len(command)+1:].split(", ")
			if not len(arg[0]):
				arg = []
			if command in self.commands.keys():
				adminCommand = getattr(self.commands[command], "__zxLoLBoT_command_admin", False)
				if (adminCommand and self.isAdmin(message["from"])) or not adminCommand: #Checks if it's an administrator-only command and if the sender is an admin
					threading.Thread(target=self.commands[command], args=(message["from"], arg)).start()
				elif self.notAdminMessage:
					self.message(message["from"], self.notAdminMessage)
			elif self.invalidCommandMessage:
				self.message(message["from"], self.invalidCommandMessage)

	def onXMPPFailedAuth(self, error):
		"""Handler for XMPP failed authentication event"""

		print("Invalid username/password provided")
		sys.exit(-1)

	def configure(self, **kwargs):
		"""Configure extra settings for the bot"""

		admin 						= kwargs.get("admin", None)
		admins 						= kwargs.get("admins", None)
		self.riotApiKey 			= kwargs.get("riotApiKey", self.riotApiKey)
		self.helpCommand 			= kwargs.get("helpCommand", self.helpCommand)
		self.notAdminMessage 		= kwargs.get("notAdminMessage", self.notAdminMessage)
		self.someoneAddedMessage 	= kwargs.get("someoneAddedMessage", self.someoneAddedMessage)
		self.someoneOnlineMessage 	= kwargs.get("someoneOnlineMessage", self.someoneOnlineMessage)
		self.invalidCommandMessage 	= kwargs.get("invalidCommandMessage", self.invalidCommandMessage)

		if isinstance(admins, list):
			for zadmin in admins:
				if zadmin not in self.admins:
					self.addAdmin(zadmin)
		if admin and admin not in self.admins:
			self.addAdmin(admin)

		if not self.helpCommand and "help" in self.commands.keys():
			print("Unregistered bot command: help")
			self.commands.pop("help", None)

	def connect(self):
		"""Attempts to connect to the XMPP server"""
		serverIp = dns.resolver.query(self.servers[self.region])
		if len(serverIp):
			if self.xmpp.connect((str(serverIp[0]), self.port), use_ssl=True):
				self.xmpp.process(block=False)
				self.xmpp.register_plugin("xep_0199") #Ping plugin
				print("Connection with the server established.")
				return True
			else:
				return False
		else:
			print("Couldn't resolve the server's A record.\nAn update may be required to continue using this.")
			sys.exit(-1)

	def message(self, to, message, newline=True):
		"""Sends a message to the specified person"""

		if newline:
			message = "~\n"+message
		self.xmpp.send_message(mto=str(to), mbody=str(message), mtype="chat")

	def messageAll(self, message, newline=True):
		"""Sends a message to everyone online."""

		if newline:
			message = "~\n"+message
		for person in self.friendsOnline:
			self.xmpp.send_message(mto=str(person), mbody=str(message), mtype="chat")

	def add_event_handler(self, eventType, function):
		"""Adds an handler for a specific event"""

		if inspect.ismethod(function):
			setattr(self, "__event_"+eventType, function)
		else:
			print("Invalid event handler being registered for event: " + eventType)

	def fireEvent(self, eventType, **kwargs):
		"""Simple event firing function"""

		if inspect.ismethod(getattr(self, "__event_"+eventType, None)):
			getattr(self, "__event_"+eventType)(kwargs)

	def setStatus(self, **kwargs):
		"""Configures variables for the status presence"""

		self.status["profileIcon"] 			= kwargs.get("profileIcon", self.status.get("profileIcon"))
		self.status["level"] 				= kwargs.get("level", self.status.get("level", 30))
		self.status["statusMsg"]			= kwargs.get("statusMsg", self.status.get("statusMsg"))
		self.status["wins"]					= kwargs.get("wins", self.status.get("wins"))
		self.status["leaves"]				= kwargs.get("leaves", self.status.get("leaves"))
		self.status["queueType"]			= kwargs.get("queueType", self.status.get("queueType"))
		self.status["rankedLeagueName"] 	= kwargs.get("rankedLeagueName", self.status.get("rankedLeagueName"))
		self.status["rankedLeagueDivision"] = kwargs.get("rankedLeagueDivision", self.status.get("rankedLeagueDivision"))
		self.status["rankedLeagueTier"]		= kwargs.get("rankedLeagueTier", self.status.get("rankedLeagueTier"))
		self.status["rankedRating"]			= kwargs.get("rankedRating", self.status.get("rankedRating"))
		self.status["rankedLosses"]			= kwargs.get("rankedLosses", self.status.get("rankedLosses"))
		self.status["rankedWins"]			= kwargs.get("rankedWins", self.status.get("rankedWins"))
		self.status["skinname"]				= kwargs.get("skinname", self.status.get("skinname"))
		self.status["gameStatus"]			= kwargs.get("gameStatus", self.status.get("gameStatus", "outOfgame"))
		self.xmpp.send_presence(ptype="chat", pstatus=self.getStatus())

	def getStatus(self):
		"""Returns the current status"""

		status = ""
		for name,value in self.status.items():
			if value != None:
				status += "<"+str(name)+">"+str(value)+"</"+str(name)+">"
		if status.find("profileIcon") == -1:
			status += "<profileIcon></profileIcon>"
		return "<body>"+status+"</body>"

	def summonerIdToName(self, summonerId):
		"""Tries getting the name of a summoner from their id using the riot api
		This requires self.riotApiKey to be configured using self.configure
		Returns none if an error was found"""

		if self.riotApiKey:
			try:
				source = urllib.request.urlopen("http://prod.api.pvp.net/api/lol/"+urllib.parse.quote(self.region.lower())+"/v1.4/summoner/"+urllib.parse.quote(str(summonerId))+"/name?api_key="+urllib.parse.quote(self.riotApiKey))
			except urllib.error.HTTPError as err:
				if err.code == 401: #Unauthorized
						print("An api request has been attempted with an invalid riot api key.")
						print("Removing the riot api key from the configuration.")
						self.riotApiKey = None
				elif err.code == 404: #Not found
					print("An api request has been attempted while the riot api seems to be down at the moment.")
				return None
			else:
				source = source.read().decode()
				data = json.loads(source)
				if summonerId in data.keys():
					return data[summonerId]
				else:
					return None
		else:
			print("An api request has been attempted without an api key.")

	def summonerNameToId(self, summonerName):
		"""Tries getting the id of a summoner from their name usign the riot api
		This requires self.riotApiKey to be configured using self.configure
		Returns none if an error was found"""

		if self.riotApiKey:
			try:
				source = urllib.request.urlopen("http://prod.api.pvp.net/api/lol/"+urllib.parse.quote(self.region.lower())+"/v1.4/summoner/by-name/"+urllib.parse.quote(summonerName)+"?api_key="+urllib.parse.quote(self.riotApiKey)).read().decode()
			except urllib.error.HTTPError as err:
				if err.code == 401: #Unauthorized
						print("An api request has been attempted with an invalid riot api key.")
						print("Removing the riot api key from the configuration.")
						self.riotApiKey = None
				elif err.code == 404: #Not found
					print("An api request has been attempted while the riot api seems to be down at the moment.")
				return None
			else:
				data = json.loads(source)
				if summonerName.replace(" ", "").lower() in data:
					return str(data[summonerName.replace(" ", "").lower()]["id"])
				else:
					return None
		else:
			print("An api request has been attempted without an api key.")

	def jidToSummonerId(self, jid):
		"""Cuts the summonerId out of a jid and return it"""
		jid = str(jid)
		if jid[0:3] == "sum": #Valid jid containing a summonerId
			return str(jid[3:jid.find("@")])
		else:
			return None

	def isAdmin(self, jid):
		"""Checks if the summonerId within the jid is an admin"""

		summonerId = self.jidToSummonerId(jid)
		if summonerId in self.admins:
			return True
		else:
			return False
	def addAdmin(self, admin):
		"""Add an admin to the admins list.
		If the admin is numerical then we assume it's a summonerId and add it directly to the admin list.
		Otherwise if the admin has characters we assume it's a summonerName and we attempt getting the summonerId using the riot api. (Require self.riotApiKey)"""

		admin = str(admin)
		error = False
		if admin not in self.admins:
			if admin.isdigit(): #admin is more than likely a summoner id
				self.admins.append(admin)
			elif self.riotApiKey: #admin is more than likely a summoner name
				summonerId = self.summonerNameToId(admin)
				if summonerId:
					self.admins.append(summonerId)
					admin += " ("+summonerId+")"
				else:
					error = True
					print(admin + " is not a registered summoner or the riot api is down at the moment.")
			else:
				error = True
				print("An api request has been attempted without an api key.")
		else:
			error = True
			print("Attempted to add an admin that is already an admin.")
		if not error:
			print(admin + " has been added to the admins list.")

	def removeAdmin(self, admin):
		"""Removes an admin from the admins list."""

		admin = str(admin)
		if admin in self.admins:
			self.admins.remove(admin)
			print(admin + " has been removed from the admins list.")
		else:
			print("Attempted to remove an admin that is not an admin.")

	@botcommand
	def help(self, sender, arg):
		"""Returns help for commands"""

		isAdmin = self.isAdmin(sender)
		reply = ""

		#Help for a single command
		if len(arg):
			if arg[0] in self.commands.keys(): #Valid command
				hiddenCommand = getattr(self.commands[arg[0]], "__zxLoLBoT_command_hidden", False)
				adminCommand  = getattr(self.commands[arg[0]], "__zxLoLBoT_command_admin", False)
				if (adminCommand and isAdmin) or (not hiddenCommand and not adminCommand) or (hiddenCommand and isAdmin):
					doc = self.commands[arg[0]].__doc__ or "No description available"
					reply = "Documentation for: " + arg[0] + "\n " + doc.replace("\t", "").replace("\n", "\n ")
		#Help for all commands
		else:
			reply += "List of available commands:\n "
			for command in sorted(self.commands):
				hiddenCommand = getattr(self.commands[command], "__zxLoLBoT_command_hidden", False)
				adminCommand  = getattr(self.commands[command], "__zxLoLBoT_command_admin", False)
				if (adminCommand and isAdmin) or (not hiddenCommand and not adminCommand) or (hiddenCommand and isAdmin):
					doc = self.commands[command].__doc__ or "No description available"
					if doc != "No description available":
						doc = doc.split("\n")[0]
					reply += command + " - " + doc + "\n "
		if reply:
			self.message(sender, reply)
		else:
			self.message(sender, "There is no command called: " + arg[0])