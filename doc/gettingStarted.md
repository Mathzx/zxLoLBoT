#Getting started
First of all import zxlolbot

```python
import zxlolbot
```

Then create your bot's class and inherit it with zxlolbot

```python
class helloworld(zxlolbot.zxLoLBoT):
    def __init__(self, username, password, region="NA"):
        zxlolbot.zxLoLBoT.__init__(self, username, password, region)
```

At this point you can create commands by decoration zxlolbot.botcommand:

```python
@zxlolbot.botcommand
def hello(self, sender, args):
    """Replies hello to the sender"""
    self.message(sender, "Hello world !")
```

You can also add events using add_event_handler:
```python
self.add_event_handler("message", self.on_message)
```

Then creating onMessage:

```python
def on_message(self, args):
    """Handler for message event"""
    print(args["sender"] + ": " + args["message"])
```

Then it's a matter of initializing the class and connecting it

```python
bot = helloworld("username", "password)
bot.connect()
```

Complete code:

```python
import zxlolbot
class helloworld(zxlolbot.zxLoLBoT):
    def __init__(self, username, password, region="NA"):
        zxlolbot.zxLoLBoT.__init__(self, username, password, region)
        self.add_event_handler("message", self.on_message)

    def on_message(self, args):
        """Handler for message event"""
        print(args["sender"] + ": " + args["message"])

    @zxlolbot.botcommand
    def hello(self, sender, args):
        """Replies hello to the sender"""
        self.message(sender, "Hello world !")
bot = helloworld("username", "password")
bot.connect()
```

###More info in the documentation:
* [List of functions](functions.md)
* [Creating status](status.md)
* [More about the decorator botcommand](decorator.md)
* [Using events](events.md)
* [Using the riot api](riotapi.md)
* [Configure extra settings](configure.md)
* [Examples](../examples)