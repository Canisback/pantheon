# Pantheon

Simple library to use the Riot API with Python Asyncio.

Supports all endpoints except static data and the tournaments ones (and matchs by tournament code).

It has an efficient rate limiting system as well as an error handler that automatically resend request on when needed.

Currently supported requests : 
 * champion masteries by summonerId -> getChampionMasteries(summonerId)
 * champion masteries by summonerId and championId -> getChampionMasteriesByChampionId(summonerId,championId)
 * champion masteries score by summonerId -> getChampionMasteriesScore(summonerId)
 * champions -> getChampions()
 * champions by championId -> getChampionsById(championId)
 * league by leagueId -> getLeagueById(leagueId)
 * league position by summonerId -> getLeaguePosition(summonerId)
 * challenger league by queue (optional) -> getChallengerLeague(queue)
 * lol status -> getStatus()
 * master league by queue (optional) -> getMasterLeague(queue)
 * match by matchId -> getMatch(matchId)
 * match timeline by matchId -> getTimeline(matchId)
 * matchlist by accountId (with parameters) -> getMatchlist(self, accountId, params) / params={"queue":420","season":11}
 * current game by summonerId -> getCurrentGame(summonerId)
 * summoner by summonerId -> getSummoner(summonerId)
 * summoner by accountId -> getSummonerByAccountId(accountId)
 * summoner by name -> getSummonerByName(name)
 * third party code by summonerId -> getThirdPartyCode(summonerId)

Further requests supported and documentation (hopefully) incoming
