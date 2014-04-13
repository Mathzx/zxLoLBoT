#Configure
You can make certain changes to the bot using configure.

```python
import zxlolbot
bot = zxlolbot.zxLoLBoT("username", "password")
bot.configure(help_command=False)
bot.connect()
```

The example above would disable the help command. Keep in mind you can also unregister the help command using:

```python
bot.unregister_command("help")
```

List of parameters:

* **admin** - the summoner ID of someone able to run admin commands. Summoner Names can be used instead if a riot api key is provided.
* **admins** - Same as above except for lists of admins.
* **riot_api_key** - Riot api developper key. More about it in the documentation. ([Riot api](#))
* **help_command** - Disable the help command
* **not_admin_message** - The message to send when someone tries to use an admin command but isn't an admin. Default is None
* **someone_added_message** - The message to send when someone added you and logs on for the first time. Default is Thank you for adding me.\nType help to start
* **someone_online_message** - The message to send when someone logs on. Also sends this to everyone after logging on. Default is None
* **invalid_command_message** - The message to send when someone says something or uses a command that doesn,t exist. Default is None. **%COMMAND%** gets replaced by the name of the command.
* **need_arg_message** - The message to send when someone uses a command that was configured with need_arg. If set to none. **%COMMAND%** gets replaced by the name of the command.