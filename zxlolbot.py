#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
An easy to use framework for writing league of legends chat bots using the xmpp protocol.
"""

import sys
import json
import inspect
import logging
import threading
import urllib.error
import urllib.parse
import urllib.request

try:
    import sleekxmpp
except ImportError:
    logging.getLogger(__name__).fatal("You need to install sleekxmpp from http://sleekxmpp.com")
    sys.exit(-1)
try:
    import dns
except ImportError:
    logging.getLogger(__name__).fatal("You need to install dnspython from http://www.dnspython.org")
    sys.exit(-1)

logging.getLogger('sleekxmpp').setLevel(logging.WARNING) #Gets rid of sleekxmpp logging unless important

def botcommand(*args, **kwargs):
    """Decorator for bot command function"""

    def decorate(function, hidden=False, admin=False, name=None, need_arg=False):
        function._zxLoLBoT_command = True
        function._zxLoLBoT_command_name = name or function.__name__
        function._zxLoLBoT_command_admin = admin
        function._zxLoLBoT_command_hidden = hidden
        function._zxLoLBoT_command_need_arg = need_arg
        return function

    if args:
        return decorate(args[0], **kwargs)
    else:
        return lambda function: decorate(function, **kwargs)

class zxLoLBoT():
    def __init__(self, username, password, region="NA"):
        """Initializes the bot and sets up commands."""

        #XMPP
        self.xmpp                       = sleekxmpp.ClientXMPP(username+"@pvp.net/xiff", "AIR_"+password)

        #Server
        self.server                     = 'chat.%REGION%.lol.riotgames.com'
        self.regions                    = {"BR":"br", "EUN": "eun1",
                                           "EUW": "eu", "NA": "na1",
                                           "KR": "kr", "OCE": "oc1",
                                           "RU": "ru", "TR": "tr"}
        self.port                       = 5223
        
        #Account
        self.username                   = username
        self.password                   = password
        self.riot_api_key               = None
        self.region                     = region
        self.recently_added             = []
        self.friends                    = []
        self.friends_online             = [] #TODO: something to do with this
        self.status                     = {}
        self.admins                     = []

        #Commands
        self.help_command               = True
        self.commands                   = {}

        #Misc
        self.summoner_ids_to_name       = {}
        self.logger                     = logging.getLogger(__name__)

        #Custom messages
        self.not_admin_message          = None
        self.someone_added_message      = "Thank you for adding me.\nType help to start"
        self.someone_online_message     = None
        self.invalid_command_message    = None
        self.need_arg_message           = "Invalid usage of %COMMAND%\nPlease use help %COMMAND%"
        self.room_invite_message        = "I'm sorry, I don't join private rooms!"

        #XMPP Events
        self.xmpp.add_event_handler("presence_unsubscribe", self.on_xmpp_presence_unsubscribe)
        self.xmpp.add_event_handler("presence_subscribe", self.on_xmpp_presence_subscribe)
        self.xmpp.add_event_handler("failed_auth", self.on_xmpp_failed_auth)
        self.xmpp.add_event_handler("got_offline", self.on_xmpp_got_offline)
        self.xmpp.add_event_handler("got_online", self.on_xmpp_got_online)
        self.xmpp.add_event_handler("session_start", self.on_xmpp_start)
        self.xmpp.add_event_handler("disconnected", self.on_xmpp_disconnected)
        self.xmpp.add_event_handler("message", self.on_xmpp_message)
        self.xmpp.add_event_handler("roster_update", self.on_xmpp_roster_update, disposable=True)
        self.xmpp.add_event_handler("groupchat_invite", None) #Ends up goign to on_xmpp_message

        #Testing region and registering commands
        if region.upper() not in self.regions:
            self.logger.critical("Invalid region.(only " + ", ".join(self.regions.keys())+" are accepted)")
            sys.exit(-1)
        for name, value in inspect.getmembers(self):
            if callable(value) and hasattr(value, "_zxLoLBoT_command"):
                name = value._zxLoLBoT_command_name
                self.commands[name] = value
                self.logger.debug("Registered bot command: " + name)

    def on_xmpp_roster_update(self, roster):
        """Handler for roster update event"""
        for item in roster["roster"]["items"]:
            if item not in self.friends:
                self.friends.append(self.jid_to_summoner_id(item))
        if self.friends:
            self.fire_event("got_friendlist", friends=self.friends)

    def on_xmpp_presence_subscribe(self, presence):
        """Handler for XMPP presence subscribes"""
        self.recently_added.append(str(presence["from"])+"/xiff")
        summoner_id = self.jid_to_summoner_id(presence["from"])
        if self.riot_api_key:
            if summoner_id not in self.summoner_ids_to_name:
                self.summoner_ids_to_name[summoner_id] = self.summoner_id_to_name(summoner_id)
            self.fire_event("someone_added", who=str(presence["from"]), summoner_name=self.summoner_ids_to_name[summoner_id])
            self.logger.debug(self.summoner_ids_to_name[summoner_id] + " just added you")
        else:
            self.fire_event("someone_added", who=str(presence["from"]))
            self.logger.debug(str(presence["from"]) + " just added you")
        if summoner_id not in self.friends:
            self.friends.append(summoner_id)

    def on_xmpp_presence_unsubscribe(self, presence):
        """Handler for XMPP presence unsubscribes"""

        summoner_id = self.jid_to_summoner_id(presence["from"])
        if self.riot_api_key and summoner_id in self.summoner_ids_to_name:
            self.fire_event("someone_removed", who=str(presence["from"]), summoner_name=self.summoner_ids_to_name[summoner_id])
            self.logger.debug(self.summoner_ids_to_name[summoner_id] + " just removed you")
            self.summoner_ids_to_name.pop(str(summoner_id), None)
        else:
            self.logger.debug(str(presence["from"]) + " just removed you")
            self.fire_event("someone_removed", who=str(presence["from"]))
        if summoner_id in self.friends:
            self.friends.remove(summoner_id)

    def on_xmpp_start(self, e):
        """Handler for XMPP session start event"""

        self.xmpp.get_roster()
        self.xmpp.send_presence(ptype="chat", pstatus=self.get_status())
        self.logger.info("Successfully logged in")
        self.fire_event("got_online")

    def on_xmpp_disconnected(self, e):
        """Handler for XMPP disconnected event"""

        self.fire_event("got_offline")

    def on_xmpp_got_online(self, presence):
        """Handler for XMPP got online event"""

        if presence["from"] != self.xmpp.boundjid:
            self.friends_online.append(str(presence["from"]))
            self.xmpp.send_presence(pto=presence["from"], ptype="chat", pstatus=self.get_status())
            self.fire_event("someone_online", who=str(presence["from"]))
            if presence["from"] in self.recently_added:
                self.recently_added.remove(presence["from"])
                if self.someone_added_message:
                    self.message(presence["from"], self.someone_added_message)
                self.fire_event("someone_added_online", who=str(presence["from"]))
            else: #Only send either recently_added or just logged on message
                if self.someone_online_message:
                    self.message(presence["from"], self.someone_online_message)

    def on_xmpp_got_offline(self, presence):
        """Handler for XMPP got offline event"""

        if str(presence["from"]) in self.friends_online:
            self.friends_online.remove(str(presence["from"]))
            self.fire_event("someone_offline", who=str(presence["from"]))

    def on_xmpp_message(self, message):
        """Handler for XMPP incoming messages event"""

        if message["type"] == "chat":
            sender = str(message["from"])
            msg = message["body"]
            #Command handling
            command     = msg.split()[0]
            args         = msg[len(command)+1:].split(", ")
            if not args[0]:
                args = []
            if command in self.commands:
                adminCommand = getattr(self.commands[command], "_zxLoLBoT_command_admin", False)
                 #Checks if it's an administrator-only command and if the sender is an admin
                if (adminCommand and self.is_admin(sender)) or not adminCommand:
                    if getattr(self.commands[command], "_zxLoLBoT_command_need_arg", False) and not args:
                        if self.need_arg_message:
                            self.message(sender, self.need_arg_message.replace("%COMMAND%", command))
                    else:
                        threading.Thread(target=self.commands[command], args=(sender, args)).start()
                elif self.not_admin_message:
                    self.message(sender, self.not_admin_message)
            elif self.invalid_command_message:
                self.message(sender, self.invalid_command_message.replace("%COMMAND%", command))

            #Event handling
            summoner_id = self.jid_to_summoner_id(sender)
            if self.riot_api_key:
                if summoner_id not in self.summoner_ids_to_name:
                    self.summoner_ids_to_name[summoner_id] = self.summoner_id_to_name(summoner_id)
                self.fire_event("message", sender=sender, message=msg, summoner_id=summoner_id, summoner_name=self.summoner_ids_to_name[summoner_id])
            else:
                self.fire_event("message", sender=sender, message=msg, summoner_id=summoner_id)
        elif message["type"] == "normal" and str(message["from"])[2:3] == "~": #Groupchat invite
            inviter = message["body"][0:message["body"].find(" ")]
            if self.room_invite_message:
                self.message(inviter, self.room_invite_message)

    def on_xmpp_failed_auth(self, error):
        """Handler for XMPP failed authentication event"""

        self.logger.fatal("Invalid username/password provided")
        self.fire_event("failed_auth")
        sys.exit(-1)

    def configure(self, **kwargs):
        """Configure extra settings for the bot"""

        admin                        = kwargs.get("admin", None)
        admins                       = kwargs.get("admins", None)
        self.riot_api_key            = kwargs.get("riot_api_key", self.riot_api_key)
        self.help_command            = kwargs.get("help_command", self.help_command)
        self.not_admin_message       = kwargs.get("not_admin_message", self.not_admin_message)
        self.someone_added_message   = kwargs.get("someone_added_message", self.someone_added_message)
        self.someone_online_message  = kwargs.get("someone_online_message", self.someone_online_message)
        self.invalid_command_message = kwargs.get("invalid_command_message", self.invalid_command_message)
        self.need_arg_message        = kwargs.get("need_arg_message", self.need_arg_message)
        self.room_invite_message     = kwargs.get("room_invite_message", self.room_invite_message)

        if isinstance(admins, list):
            for zadmin in admins:
                if zadmin not in self.admins:
                    self.add_admin(zadmin)
        if admin and admin not in self.admins:
            self.add_admin(admin)

        if not self.help_command and "help" in self.commands:
            self.logger.debug("Unregistered bot command: help")
            self.commands.pop("help", None)

    def connect(self):
        """Attempts to connect to the XMPP server"""
        serverIp = dns.resolver.query(self.server.replace("%REGION%", self.regions[self.region.upper()]))
        if serverIp:
            if self.xmpp.connect((str(serverIp[0]), self.port), use_ssl=True):
                self.xmpp.process(block=False)
                self.xmpp.register_plugin("xep_0199") #Ping plugin
                self.logger.debug("Connection with the server established.")
                return True
            else:
                self.logger.critical("Couldn't resolve the server's A record.\nAn update may be required to continue using this.")
                sys.exit(-1)
        else:
            self.logger.critical("Couldn't resolve the server's A record.\nAn update may be required to continue using this.")
            sys.exit(-1)

    def message(self, to, message, newline=True):
        """Sends a message to the specified person"""

        if newline:
            message = "~\n"+message
        self.xmpp.send_message(mto=str(to), mbody=str(message), mtype="chat")

    def message_all(self, message, newline=True):
        """Sends a message to everyone online."""

        if newline:
            message = "~\n"+message
        for person in self.friends_online:
            self.xmpp.send_message(mto=str(person), mbody=str(message), mtype="chat")

    def add_event_handler(self, event_type, function):
        """Adds an handler for a specific event"""

        if callable(function):
            setattr(self, "_event_"+event_type, function)
        else:
            self.logger.warning("Invalid event handler being registered for event: " + event_type)

    def fire_event(self, event_type, **kwargs):
        """Simple event firing function"""

        if callable(getattr(self, "_event_"+event_type, None)):
            if kwargs.items():
                getattr(self, "_event_"+event_type)(kwargs)
            else:
                getattr(self, "_event_"+event_type)()

    def set_status(self, **kwargs):
        """Configures variables for the status presence"""

        self.status["wins"]                 = kwargs.get("wins", self.status.get("wins"))
        self.status["level"]                = kwargs.get("level", self.status.get("level", 30))
        self.status["leaves"]               = kwargs.get("leaves", self.status.get("leaves"))
        self.status["skinname"]             = kwargs.get("skinname", self.status.get("skinname"))
        self.status["queueType"]            = kwargs.get("queue_type", self.status.get("queueType"))
        self.status["statusMsg"]            = kwargs.get("status_msg", self.status.get("statusMsg"))
        self.status["rankedWins"]           = kwargs.get("ranked_wins", self.status.get("rankedWins"))
        self.status["profileIcon"]          = kwargs.get("profile_icon", self.status.get("profileIcon"))
        self.status["rankedLosses"]         = kwargs.get("ranked_losses", self.status.get("rankedLosses"))
        self.status["rankedRating"]         = kwargs.get("ranked_rating", self.status.get("rankedRating"))
        self.status["rankedLeagueName"]     = kwargs.get("ranked_league_name", self.status.get("rankedLeagueName"))
        self.status["rankedLeagueTier"]     = kwargs.get("ranked_league_tier", self.status.get("rankedLeagueTier"))
        self.status["gameStatus"]           = kwargs.get("game_status", self.status.get("gameStatus", "outOfgame"))
        self.status["rankedLeagueDivision"] = kwargs.get("ranked_league_division", self.status.get("rankedLeagueDivision"))
        
        self.xmpp.send_presence(ptype="chat", pstatus=self.get_status())

    def get_status(self):
        """Returns the current status"""

        status = ""
        for name,value in self.status.items():
            if value != None:
                status += "<"+str(name)+">"+str(value)+"</"+str(name)+">"
        if status.find("profileIcon") == -1:
            status += "<profileIcon></profileIcon>"
        return "<body>"+status+"</body>"

    def summoner_id_to_name(self, summoner_id):
        """Tries getting the name of a summoner from their id using the riot api
        This requires self.riot_api_key to be configured using self.configure
        Returns none if an error was found"""

        if self.riot_api_key:
            try:
                source = urllib.request.urlopen("http://prod.api.pvp.net/api/lol/"+
                                                urllib.parse.quote(self.region.lower())+
                                                "/v1.4/summoner/"+
                                                urllib.parse.quote(str(summoner_id))
                                                +"/name?api_key="+urllib.parse.quote(self.riot_api_key))
            except urllib.error.HTTPError as err:
                if err.code == 401: #Unauthorized
                        self.logger.warning("An api request has been attempted with an invalid riot api key.")
                        self.logger.debug("Removing the riot api key from the configuration.")
                        self.riot_api_key = None
                elif err.code == 404: #Not found
                    self.logger.debug("An api request has been attempted while the riot api seems to be down at the moment.")
                return None
            else:
                source = source.read().decode()
                data = json.loads(source)
                return data.get(summoner_id)
        else:
            self.logger.warning("An api request has been attempted without an api key.")

    def summoner_name_to_id(self, summoner_name):
        """Tries getting the id of a summoner from their name usign the riot api
        This requires self.riot_api_key to be configured using self.configure
        Returns none if an error was found"""

        if self.riot_api_key:
            try:
                source = urllib.request.urlopen("http://prod.api.pvp.net/api/lol/"+
                                                urllib.parse.quote(self.region.lower())+
                                                "/v1.4/summoner/by-name/"+
                                                urllib.parse.quote(summoner_name)+
                                                "?api_key="+urllib.parse.quote(self.riot_api_key)).read().decode()
            except urllib.error.HTTPError as err:
                if err.code == 401: #Unauthorized
                        self.logger.warning("An api request has been attempted with an invalid riot api key.")
                        self.logger.debug("Removing the riot api key from the configuration.")
                        self.riot_api_key = None
                elif err.code == 404: #Not found
                    self.logger.debug("An api request has been attempted while the riot api seems to be down at the moment.")
                return None
            else:
                data = json.loads(source)
                if summoner_name.replace(" ", "").lower() in data:
                    return str(data[summoner_name.replace(" ", "").lower()]["id"])
                else:
                    return None

        else:
            self.logger.warning("An api request has been attempted without an api key.")

    def has_riot_api_key(self):
        """Returns true if a riot api key has been configured, false otherwise"""

        return self.riot_api_key

    def jid_to_summoner_id(self, jid):
        """Cuts the summoner_id out of a jid and return it"""

        jid = str(jid)
        if jid[0:3] == "sum": #Valid jid containing a summoner_id
            return str(jid[3:jid.find("@")])
        else:
            return None

    def get_friends_online(self):
        """Returns a list of summoner ids for online friends"""

        return self.friends_online
    def get_friends(self):
        """Returns a list of summoner ids for all your friends"""

        return self.friends

    def get_admins(self):
        """Returns a list of summoner ids for the admins"""

        return self.admins

    def is_admin(self, jid):
        """Checks if the summoner_id within the jid is an admin"""

        return self.jid_to_summoner_id(jid) in self.admins

    def add_admin(self, admin):
        """Add an admin to the admins list.
        If the admin is numerical then we assume it's a summoner_id and add it directly to the admin list.
        If the admin has characters we assume it's a summoner_name and we attempt getting the summoner_id using the riot api.
        (Require self.riot_api_key)"""

        admin = str(admin)
        error = False
        if admin not in self.admins:
            if admin.isdigit(): #admin is more than likely a summoner id
                self.admins.append(admin)
            elif self.riot_api_key: #admin is more than likely a summoner name
                summoner_id = self.summoner_name_to_id(admin)
                if summoner_id:
                    self.admins.append(summoner_id)
                    admin += " ("+str(summoner_id)+")"
                else:
                    error = True
                    self.logger.debug(admin + " is not a registered summoner or the riot api is down at the moment.")
            else:
                error = True
                self.logger.warning("An api request has been attempted without an api key.")
        else:
            error = True
            self.logger.warning("Attempted to add an admin that is already an admin.")
        if not error:
            self.logger.debug(admin + " has been added to the admins list.")

    def remove_admin(self, admin):
        """Removes an admin from the admins list."""

        admin = str(admin)
        if admin in self.admins:
            self.admins.remove(admin)
            self.logger.debug(admin + " has been removed from the admins list.")
        else:
            self.logger.debug("Attempted to remove an admin that is not an admin.")

    def unregister_command(self, command_name):
        """Unregisters a command from an handler"""

        if command_name in self.commands:
            self.commands.pop(command_name, None)
            self.logger.debug("Unregistered bot command: " + command_name)
        else:
            self.logger.warning("Tried to unregister a command called " + command_name + " that isn't registered yet")
    @botcommand
    def help(self, sender, arg):
        """Returns help for commands
        Usage: help or help <command>
        Example: help or help mmr"""
        is_admin = self.is_admin(sender)
        reply = ""

        #Help for a single command
        if arg:
            if arg[0] in self.commands: #Valid command
                hiddenCommand = getattr(self.commands[arg[0]], "_zxLoLBoT_command_hidden", False)
                adminCommand  = getattr(self.commands[arg[0]], "_zxLoLBoT_command_admin", False)
                if (adminCommand and is_admin) or (not hiddenCommand and not adminCommand) or (hiddenCommand and is_admin):
                    doc = self.commands[arg[0]].__doc__ or "No description available"
                    reply = "Documentation for: " + arg[0] + "\n " + doc.replace("\t", "").replace("\n", "\n ").replace("    ", "")
        #Help for all commands
        else:
            reply += "List of available commands:\n "
            for command in sorted(self.commands):
                hiddenCommand = getattr(self.commands[command], "_zxLoLBoT_command_hidden", False)
                adminCommand  = getattr(self.commands[command], "_zxLoLBoT_command_admin", False)
                if (adminCommand and is_admin) or (not hiddenCommand and not adminCommand) or (hiddenCommand and is_admin):
                    doc = self.commands[command].__doc__ or "No description available"
                    if doc != "No description available":
                        doc = doc.split("\n")[0]
                    reply += command + " - " + doc + "\n "
        if reply:
            self.message(sender, reply)
        else:
            self.message(sender, "There is no command called: " + arg[0])