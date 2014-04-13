import zxlolbot

class echobot(zxlolbot.zxLoLBoT):
	def __init__(self, username, password, region="NA"):
		zxlolbot.zxLoLBoT.__init__(self, username, password, region)
		self.add_event_handler("message", self.on_message)

	def on_message(self, args):
		"""Handler for the message event.
		args is a dictionary with specific keys.
		args["sender"]  - The JID of the person the message is coming from.
		args["message"] - The message.
		args["summoner_id"] - The summoner ID of the person the message is coming from."""
		self.message(args["sender"], args["message"], False)

if __name__ == "__main__":
	bot = echobot("username", "password")
	bot.connect()