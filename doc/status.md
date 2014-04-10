#Status
Creating a status:

    import zxlolbot

    bot = zxlolbot.zxLoLBoT("username", "password")
    bot.connect()
    bot.setStatus(level=30, statusMsg="Version 1.0")
![](statusBasic.PNG)

List of available parameters:

* profileIcon - This doesn't actually change your icon but it should. I need to check into it
* level - Self explanatory. Can be any number, even negative ones.
* statusMsg - Text under the username in the friendlist
* wins - Self explanatory. Can be any number, not negative ones. Maximum 1329790976
* leaves - Self explanatory. Can be any number, not negative ones.
* queueType - Highest queue type to display stats from. Not required to spoof a rating.
* rankedLeagueName - Name of your ranked league. Must be a valid one or it will start with ** and spaces won't work.
* rankedLeagueDivision - Can be either I, II, III, IV, V
* rankedLeagueTier - Can be either: UNRANKED, BRONZE, SILVER, GOLD, PLATINUM, DIAMOND, CHALLENGER
* rankedRating - Rating to be shown in game lobby. Obsolete at the moment.
* rankedLosses - Amount of ranked losses. Obsolete at the moment.
* rankedWins - Amount of ranked wins. Obsolete at the moment.
* skinname - Name of the champion you are playing if gameStatus is inGame
* gameStatus - Can be either: inGame, outOfgame

setStatus remembers your previous status settings. You don't have to include all previous one you've made to newer one if for example you just wanna change statusMsg.

You can spoof most of the data above, Example:

![](statusSpoof.PNG)
