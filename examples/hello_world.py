import zxlolbot

class helloworld(zxlolbot.zxLoLBoT):
	def __init__(self, username, password, region="NA"):
		zxlolbot.zxLoLBoT.__init__(self, username, password, region)
	@zxlolbot.botcommand
	def hello(self, sender, args):
		"""Replies Hello world to the sender
		Usage: hello
		Example: hello"""
		self.message(sender, "Hello world")
if __name__ == "__main__":
	bot = helloworld("username", "password")
	bot.connect()