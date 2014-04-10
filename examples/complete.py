import zxlolbot

botcommand = zxlolbot.botcommand
class MyBot(zxlolbot.zxLoLBoT):
	def __init__(self, username, password, region="NA"):
		zxlolbot.zxLoLBoT.__init__(self, username, password, region="NA")

	@botcommand(hidden=True)
	def secret(self, sender, args):
		"""This command won't be shown in help command""" #Unless you're an admin
		self.message(sender, "How did you know this very secret command?")

	@botcommand(admin=True)
	def putstatus(self, sender, args):
		"""Admin commands are hidden automatically.""" #Unless you're an admin
		if len(args):
			self.setStatus(statusMsg=args[0])
			self.message(sender, "My new status is now: " + args[0])
		else:
			self.message(sender, "You need to tell me what to change it to!")
	@botcommand(admin=True)
	def broadcast(self, sender, args):
		"""Sends a message to everyone online"""
		if len(args):
			self.messageAll(args[0])
		else:
			self.message(sender, "I need to know what to broadcast!")

	#Help command will generate a description by itself since this function doesn't have a docstring
	#Adds the sum of all args
	#usage: sum 3, 2, 5, 6, 7 or sum 3+2+5+6+7
	#output: Sum(3+2+5+6+7) = 23
	@botcommand
	def sum(self, sender, args):
		sum = 0
		if len(args) > 1: #Regular usage of args. separated by ", "
			for arg in args:
				if arg.isdigit():
					sum += int(arg)
		elif len(args) == 1: #Only 1 arg. Custom separation with "+"
			numbers = args[0].split("+")
			for number in numbers:
				if number.isdigit():
					sum += int(number)
		if sum:
			self.message(sender, "Sum("+"+".join(args)+") = " + str(sum))
		else:
			self.message(sender, "No valid numbers were given")
if __name__ == "__main__":
	bot = MyBot("USERNAME", "PASSWORD")
	bot.configure(invalidCommandMessage="This is not a valid command.\nType help for help", admin="SUMMONER_ID", notAdminMessage="I'm sorry but I can't do that for you")
	bot.connect()
	bot.setStatus(wins=13, statusMsg="Version 1.0", rankedLeagueTier="BRONZE", rankedLeagueDivision="V", rankedLeagueName="Jarvan IV's Liberators")