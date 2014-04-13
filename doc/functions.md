#List of functions

###connect()
Connects to the server and logs on.
###configure(**kwargs)
More about [configure](doc/configure.md) in the documentation.
###message(to, message, newline=True)
* **to** - JID of the person you want to message
* **message** - self explanatory
* **newline** - If set to true, the message will start with ~\n

###message_all(message, newline)
* **message** - self explanatory
* **newline** - If set to true, the message wil start with ~\n

###add_event_handler(event_type, handler)
More about [events](doc/events.md) in the documentation.
###set_status(**kwargs)
More about [status](doc/status.md) in the documentation.
###summoner_id_to_name(summoner_id)
Requires a riot api key to be configured using [configure](doc/configure)

More about [riot api](doc/riotapi.md) in the documentation.

Returns the summoner Name if found, None otherwise
###summoner_name_to_id(summoner_name)
Requires a riot api key to be configured using [configure](doc/configure)

More about [riot api](doc/riotapi.md) in the documentation.

Returns the summoner Id if found, None otherwise
###jid_to_summoner_id(jid)
Returns the summonerId out of a jid if there's one, None otherwise.
###is_admin(jid)
Returns True if jid is an admin, False otherwise.
###add_admin(admin)
Adds an administrator to the bot.

admin has to be a summoner Id,

If a riot api key was provided, admin can be a name.
###remove_admin(admin)
Mostly the same as above except it removes it instead of adding it.
###get_admins()
Returns the list of admins (Summoner ids)
###get_friends_online()
Returns the list of onlien friends (Summoner ids)
###unregister_command(command_name)
Unregisters a command.
###has_riot_api_key()
Returns true if a riot api key was provided, false otherwise.