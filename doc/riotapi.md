#Riot api
Well first of all to uset his riot api you need to get yourself a developper key.

You can get one by signing up [here](https://developer.riotgames.com).

Once you get your key, you can use it with your bot using the [configure](doc/configure.md) method.

	bot.configure(riotApiKey="YOUR_API_HERE")

###summonerIdToName(summonerId)
Returns the name if the id is valid, otherwise it returns None
###summonerNameToId(summonerName)
Returns the id if the name is valid, otherwise it returns None

You can also convert JIDs to summoner ID using jidToSummonerId. Returns the summoner ID if one is found otherwise it returns None.