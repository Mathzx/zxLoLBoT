#Getting started
First of all import zxlolbot

    import zxlolbot
Then create your bot's class and inherit it with zxlolbot

    class helloworld(zxlolbot.zxLoLBoT):
        def __init__(self, username, password, region="NA"):
            zxlolbot.zxLoLBoT.__init__(self, username, password, region)

At this point you can create commands by decoration zxlolbot.botcommand:

    @zxlolbot.botcommand
    def hello(self, sender, args):
        """Replies hello to the sender"""
        self.message(sender, "Hello world !")

You can also add events using add_event_handler:

    self.add_event_handler("message", self.onMessage)
Then creating onMessage:

    def onMessage(self, args):
        """Handler for message event"""
        print(args["sender"] + ": " + args["message"])
Then it's a matter of initializing the class and connecting it

    bot = helloworld("username", "password)
    bot.connect()
Complete code:

    import zxlolbot
    class helloworld(zxlolbot.zxLoLBoT):
        def __init__(self, username, password, region="NA"):
            zxlolbot.zxLoLBoT.__init__(self, username, password, region)
            self.add_event_handler("message", self.onMessage)

        def onMessage(self, args):
            """Handler for message event"""
            print(args["sender"] + ": " + args["message"])

        @zxlolbot.botcommand
        def hello(self, sender, args):
            """Replies hello to the sender"""
            self.message(sender, "Hello world !")
    bot = helloworld("username", "password")
    bot.connect()

###More info in the documentation:
* [List of functions](functions.md)
* [Creating status](status.md)
* [More about the decorator botcommand](decorator.md)
* [Using events](events.md)
* [Using the riot api](riotapi.md)
* [Configure extra settings](configure.md)
* [Examples](../examples)