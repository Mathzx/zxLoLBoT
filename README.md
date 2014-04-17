#zxLoLBoT
An easy to use framework for writing league of legends chat bots using the xmpp protocol.
###Requires:
* sleekxmpp ([Download here](http://sleekxmpp.com))
* dnspython ([Download here](http://dnspython.org))

###Setup
Just add zxlolbot.py to your project.

###Documentation:
* [Getting started](doc/gettingStarted.md)
* [Decorator botcommand](doc/decorator.md)
* [Events](doc/events.md)
* [Configuration](doc/configure.md)
* [Status](doc/status.md)
* [Riot api](doc/riotapi.md)
* [List of functions](doc/functions.md)
* [Examples](examples/)

###Demo
I made a somewhat simple bot as a demo using this framework.

Feel free to add him on league of legends north america, his name is **zxLoLBoT**

I also took the time to show how easy it would be to create a widget showing the last 20 messages the bot received.

[Demo widget](http://mathzx.com/zxlolbot.php)
###Examples
####Basic hello world bot
```python
import zxlolbot

class example(zxlolbot.zxLoLBoT):
	def __init__(self, username, password, region="NA"):
		zxlolbot.zxLoLBoT.__init__(self, username, password, region)

	@zxlolbot.botcommand
	def hello(self, sender, args):
		"""Replies hello to the sender"""
		self.message(sender, "hello")
if __name__ == "__main__":
	bot = example("username", "password")
	bot.connect()
```
List of commands:

* hello -  Replies hello to the sender
* help - list of available commands. 

#####Explanation
Commands are created by decorating zxlolbot.botcommand. (Documentation: [Decorator botcommand](doc/decorator.md))

The help command is created automatically and lists all registered commands by the decorator.

.It uses their doctstrings as the descriptions and prints something similiar to:

	List of available commands:
	 hello - Replies hello to the sender
	 help - Returns help for commands

You can hide commands from the help command by decorating it this way:

    @botcommand(hidden=True)
Same thing for admin-only commands.

    @botcommand(admin=True)
There are more options for the decorator in the [documentation](doc/decorator.md)

You can also disable the help command with configure method. (Documentation: [Configuration](doc/configure.md)) or by [using unregister_command](doc/functions.md)
####Using events
```python
import zxlolbot

botcommand = zxlolbot.botcommand
class example(zxlolbot.zxLoLBoT):
	def __init__(self, username, password, region="NA"):
		zxlolbot.zxLoLBoT.__init__(self, username, password, region)
		self.add_event_handler("message", self.on_message)

	def on_message(self, args):
		"""Handler for the message event.
		args is a dictionary with specific keys.
		args["sender"]  - The JID of the person the message is coming from.
		args["message"] - The message.
		args["summoner_id"] - The summoner ID of the person the message is coming from."""
		print(args["summoner_id"] + " said " + args["message"])

if __name__ == "__main__":
	bot = example("username", "password")
	bot.connect()
```
####Explanation
Events are added by using add_event_handler.

A complete list of events and their args can be found in the documentation. (Documentation: [Events](doc/events.md))

Summoner ids can be converted into names if a [riot api key](https://developer.riotgames.com/) is provided in the configure method. (Documentation: [Configuration](doc/configure.md))

More info about how to use the riot api in the documentation.(Documentation: [Riot api](doc/riotapi.md))
###License
Copyright (c) 2014, Mathzx. (MIT License)

See [LICENSE](LICENCE) for more info.