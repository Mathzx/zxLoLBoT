#List of functions

###connect()
Connects to the server and logs on.
###configure(**kwargs)
More about [configure](doc/configure.md) in the documentation.
###message(to, message, newline=True)
* to: JID of the person you want to message
* message: self explanatory
* newline: If set to true, the message will start with ~\n
###message(message, newline)
* message: self explanatory
* newline: If set to true, the message wil start with ~\n
###add_event_handler(eventType, handler)
More about [events](doc/events.md) in the documentation.
###setStatus(**kwargs)
More about [status](doc/status.md) in the documentation.
###summonerIdToName(summonerId)
Requires a riot api key to be configured using [configure](doc/configure)

More about [riot api](doc/riotapi.md) in the documentation.

Returns the summoner Name if found, None otherwise
###summonerNameToId(summonerName)
Requires a riot api key to be configured using [configure](doc/configure)

More about [riot api](doc/riotapi.md) in the documentation.

Returns the summoner Id if found, None otherwise
###jidToSummonerId(jid)
Returns the summonerId out of a jid if there's one, None otherwise.
###isAdmin(jid)
Returns True if jid is an admin, False otherwise.
###addAdmin(admin)
Adds an administrator to the bot.

admin has to be a summoner Id,

If a riot api key was provided, admin can be a name.
###removeAdmin(admin)
Mostly the same as above except it removes it instead of adding it.