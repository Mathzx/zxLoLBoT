#Events
Using events is simple and only requires you to register an handler to a specific event using add_event_handler

###List of events
####message
Someone sent a message

* **sender** - JID of the person who sent the message
* **summoner_id** - Summoner ID from the person who sent the message
* **summoner_name** - This arg is only provided if a riot api key has been configured using [configure](configure.md)
* **message** - Self explanatory

####failed_auth
Invalid username/password

####got_online
You just showed up as online.

####got_offline
You just got disconnected.

####someone_online
Someone just logged on

* **who** - JID of the person who just logged on

####someone_offline
Someone just logged off

* **who** - JID of the person who just logged off

####someone_added
Someone just added you

* **who** - JID of the person who just added you.
* **summoner_name** (Optional) - Summoner name of the person who just got online.

####someone_added_online
Someone who added you just logged on for the first time.

Perfect time to message them with how the bot works. Can also be configured with someone_added_message

* **who** - JID of the person who just added you and logged on for the first time

Keep in mind that the bot auto-accepts people adding it
####someone_remove
Someone just removed you from their friendlist

* **who** - JID of the person who just removed you
* **summoner_name** (Optional) - Summoner name of the person who just got offline.
