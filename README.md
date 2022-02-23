# Pantheon

[![PyPi](https://img.shields.io/pypi/v/pantheon)](https://pypi.org/project/pantheon/)
[![Build Status](https://travis-ci.com/Canisback/pantheon.svg?branch=master)](https://travis-ci.com/Canisback/pantheon)
[![codecov](https://codecov.io/gh/Canisback/pantheon/branch/master/graph/badge.svg)](https://codecov.io/gh/Canisback/pantheon)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Canisback/pantheon.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Canisback/pantheon/context:python)
[![Downloads](https://pepy.tech/badge/pantheon)](https://pepy.tech/project/pantheon)

Simple library to use the Riot API with Python Asyncio.

Supports all endpoints.

It has an efficient rate limiting system as well as an error handler that automatically resend request when needed.

**There is no cache implemented**

**The rate limit count is only kept while the script is alive**

Currently supported requests : 
 * champion masteries by summonerId -> getChampionMasteries(summonerId)
 * champion masteries by summonerId and championId -> getChampionMasteriesByChampionId(summonerId,championId)
 * champion masteries score by summonerId -> getChampionMasteriesScore(summonerId)
 * champion rotations -> getChampionRotations()
 * league by leagueId -> getLeagueById(leagueId)
 * league pages by queue, rank and tier -> getLeaguePage(queue, tier, division, page=1)
 * league position by summonerId -> getLeaguePosition(summonerId)
 * challenger league by queue (optional) -> getChallengerLeague(queue)
 * lol status -> getStatus()
 * master league by queue (optional) -> getMasterLeague(queue)
 * match by matchId -> getMatch(matchId)
 * match timeline by matchId -> getTimeline(matchId)
 * matchlist by accountId (with parameters) -> getMatchlist(self, accountId, params) / params={"queue":420,"season":11}
 * current game by summonerId -> getCurrentGame(summonerId)
 * summoner by summonerId -> getSummoner(summonerId)
 * summoner by accountId -> getSummonerByAccountId(accountId)
 * summoner by name -> getSummonerByName(name)
 * third party code by summonerId -> getThirdPartyCode(summonerId)
 * register provider -> registerProvider(region, callback_url, stub=False)
 * register tournament -> registerTournament(providerId, name, stub=False)
 * create tournament code -> createTournamentCode(tournamentId, data, nb_codes=1, stub=False)
 * get lobby events by tournament code -> getLobbyEvents(tournamentCode, stub=False)

Further requests supported and documentation (hopefully) incoming

To install, run
```
pip install pantheon
or
pip3 install pantheon
```

or you can download it and run 

```
python setup.py install
or
python3 setup.py install
```

An example of usage to get details on the last 10 games : 

```python
from pantheon import pantheon
import asyncio

server = "euw1"
api_key = "RGAPI-XXXX"

def requestsLog(url, status, headers):
    print(url)
    print(status)
    print(headers)

panth = pantheon.Pantheon(server, api_key, errorHandling=True, requestsLoggingFunction=requestsLog, debug=True)

async def getSummonerId(name):
    try:
        data = await panth.getSummonerByName(name)
        return (data['id'],data['accountId'])
    except Exception as e:
        print(e)


async def getRecentMatchlist(accountId):
    try:
        data = await panth.getMatchlist(accountId, params={"endIndex":10})
        return data
    except Exception as e:
        print(e)

async def getRecentMatches(accountId):
    try:
        matchlist = await getRecentMatchlist(accountId)
        tasks = [panth.getMatch(match['gameId']) for match in matchlist['matches']]
        return await asyncio.gather(*tasks)
    except Exception as e:
        print(e)


name = "Canisback"

loop = asyncio.get_event_loop()  

(summonerId, accountId) = loop.run_until_complete(getSummonerId(name))
print(summonerId)
print(accountId)
print(loop.run_until_complete(getRecentMatches(accountId)))
```


**Changelog :**

 * 1.3.1 : 
     * Add a locked function to check if at least one limiter is locked

 * 1.3.0 : 
     * Add custom str function for pantheon that returns the rate limits details
     * Fixed a rate limit bug not counting a request when creating a new limit

 * 1.2.1 : 
     * Add Tournament matches endpoints

 * 1.2.0 : 
     * Add LoR match and matchlist
     * Update deprecated lock handling

 * 1.1.0 : 
     * Add support for LoR and Valorant
     * Deleting auto-handling server to region for TFT matches and LoL tournaments endpoints, will break apps using these endpoint without creating another instance of Pantheon with the correct server
     
 * 1.0.12 : 
     * Add support for Clash API

 * 1.0.9 : 
     * Clean up some code
     
 * 1.0.8 : 
     * Clean up some code and upgrading for CI

 * 1.0.7 : 
     * Added TFT API endpoints
     * Added unit tests covering almost all endpoints, rate limiter not unit tested yet

 * 1.0.6 : 
     * Fixed 415 errors

 * 1.0.5 : 
     * Updated League endpoints to match with current version
     * Added tournament endpoints (stub ones)
     
 * 1.0.4 : 
     * Added 408 error code
     
 * 1.0.3 : 
     * Updated for v4 endpoints

 * 1.0.2 : 
     * Added new getChampionRotations endpoint support
     * Deleted getChampions and getChampionsById due to deprecation of corresponding endpoints
     * Fixed the getTimestamp function for the case when the Date header is missing

 * 1.0.1 : 
     * Added a debug flag, while set at True, some messages will be printed, when the rate limiter make a request waiting because limit is reached, or when retrying after an error.
     * Added callback function for logging purpose.
     * Changed error 429 handling (rate limit) so it retries after the value sent in header
     * Added support for list in matchlist params (you can pass {"queue":[420,440]}
