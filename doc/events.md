#Events
Using events is simple and only requires you to register an handler to a specific event using add_event_handler

###List of events
####message
Someone sent a message

* sender - JID of the person who sent the message
* summonerId - Summoner ID from the person who sent the message
* summonerName - This arg is only provided if a riot api key has been configured using [configure](configure.md)
* message - Self explanatory
####gotOnline
You just showed up as online.

No arg for this one.
####gotOffline
You just got disconnected.

No arg for this one.
####someoneOnline
Someone just logged on

* who - JID of the person who just logged on
####someoneOffline
Someone just logged off

* who - JID of the person who just logged off
####someoneAdded
Someone just added you
####someoneAddedOnline
Someone who added you just logged on for the first time.

Perfect time to message them with how the bot works. Can also be configured using someoneAddedMessage

*who - JID of the person who just added you and logged on for the first time
* who - JID of the person who just added you.
Keep in mind that the bot auto-accepts people adding it
####someoneRemoved
Someone just removed you from their friendlist

* who - JID of the person who just removed you
