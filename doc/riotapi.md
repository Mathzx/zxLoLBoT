#Riot api
Well first of all to uset his riot api you need to get yourself a developper key.

You can get one by signing up [here](https://developer.riotgames.com).

Once you get your key, you can use it with your bot using the [configure](doc/configure.md) method.
```python
bot.configure(riot_api_key="YOUR_API_HERE")
```
###summoner_id_to_name(summoner_id)
Returns the name if the id is valid, otherwise it returns None
###summoner_name_to_id(summoner_name)
Returns the id if the name is valid, otherwise it returns None
###has_riot_api_key()
Returns true if an api key was configured, false otherwise.
You can also convert JIDs to summoner ID using jid_to_summoner_id. Returns the summoner ID if one is found otherwise it returns None.