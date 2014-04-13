#Decorator botcommand
The decorator botcommand is used to register commands easily.

###Example

```python
@zxlolbot.botcommand
def test(self, sender, args);
	"""Description used by the help command"""
	self.message(sender, "test")
```

Every commands requires the parameters sender and args to work.

sender: The JID of the person who sent the message. Used mostly to send messages.

args: Arguements for the commands. Every arg is separated by ", "

Example:

```python
test hello
```

args would be ['hello']

```python
test hello, world
```

args would be ['hello', 'world']

Hidden command from help:

```python
@zxlolbot.botcommand(hidden=False)
```

Admin command:

```python
@zxlolbot.botcommand(admin=True)
```

Using a name other than the method name:
```python
@zxlolbot.botcommand(name="custom")
```

Require an arguement to get executed.

```python
@zxlolbot.botcommand(need_arg=True)
```

Keep in mind that you can change the message if need_arg is set to true and a command is called without arguement by changing need_arg_message in configure.

You can obviously use more than one option at the same time