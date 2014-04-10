#Decorator botcommand
The decorator botcommand is used to register commands easily.

###Example
	@zxlolbot.botcommand
	def test(self, sender, args);
		"""Description used by the help command"""
		self.message(sender, "test")
Every commands requires the parameters sender and args to work.

sender: The JID of the person who sent the message. Used mostly to send messages.

args: Arguements for the commands. Every arg is separated by ", "

Example:

    test hello
args would be ['hello']

    test hello, world
args would be ['hello', 'world']

Hidden command from help:

    @zxlolbot.botcommand(hidden=False)
Admin command:

    @zxlolbot.botcommand(admin=True)
Using a name other than the method name:

    @zxlolbot.botcommand(name="custom")
You can obviously use more than one option at the same time