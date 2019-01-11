import asyncio, aiohttp
import json

from .utils import utils as utils
from .utils import exceptions as exc

from .RateLimit.RateLimiterManager import RateLimiterManager

class Pantheon():
    
    BASE_URL = "https://{server}.api.riotgames.com/lol/"
    
    def __init__(self, server, api_key, errorHandling = False, requestsLoggingFunction = None, debug=False):
        """
        Initialize an instance of Pantheon class
        
        :param string server: The server Pantheon will target for the requests. An instance is intended to only call one server. Use multiple instances of Pantheon to call multiples servers.
        It can take the values described there : https://developer.riotgames.com/regional-endpoints.html (euw1, na1...)
        :param string api_key: The API key needed to call the Riot API
        :param boolean errorHandling: Precise if Pantheon should autoretry after a ratelimit (429) or server error (5XX). Default is False
        """
        self._key = api_key
        self._server = server
        self._rl = RateLimiterManager(debug)
        
        self.errorHandling = errorHandling
        self.requestsLoggingFunction = requestsLoggingFunction
        self.debug = debug

    def ratelimit(func):
        """
        Decorator for rate limiting.
        It will handle the operations needed by the RateLimiterManager to assure the rate limiting and the change of limits considering the returned header.
        """
        async def waitLimit(*args, **params):
            token = await args[0]._rl.getToken(func.__name__)
            
            response = await func(*args, **params)
            
            limits = utils.getLimits(response.headers)
            timestamp = utils.getTimestamp(response.headers)
            
            await args[0]._rl.getBack(func.__name__, token, timestamp, limits)
            
            return response
            
        return waitLimit
    
    def errorHandler(func):
        """
        Decorator for handling some errors and retrying if needed.
        """
        async def _errorHandling(*args, **params):
            if not args[0].errorHandling:
                return await func(*args, **params)
            else:
                try:
                    return await func(*args, **params)
                #Errors that should be retried
                except exc.RateLimit as e:
                    if args[0].debug:
                        print(e)
                        print("Retrying")
                    i = e.waitFor()
                    while i < 6:
                        await asyncio.sleep(i)
                        try:
                            return await func(*args, **params)
                        except Exception as e:
                            if args[0].debug:
                                print(e)
                        i += 2
                    raise e
                except (exc.ServerError, exc.Timeout) as e:
                    if args[0].debug:
                        print(e)
                        print("Retrying")
                    i = 1
                    while i < 6:
                        await asyncio.sleep(i)
                        try:
                            return await func(*args, **params)
                        except (exc.Timeout, exc.ServerError) as e2:
                    
                            pass
                        i += 2
                        if args[0].debug:
                            print(e2)
                            print("Retrying")
                    print("there is no bug")
                    raise e
                except (exc.NotFound, exc.BadRequest) as e:
                    raise e
                except (exc.Forbidden, exc.Unauthorized,) as e:
                    print(e)
                    raise SystemExit(0)
                except Exception as e:
                    raise e
                
        return _errorHandling
    
    def exceptions(func):
        """
        Decorator translating status code into exceptions
        """
        async def _exceptions(*args, **params):
            
            response = await func(*args, **params)
            
            if response == None:
                raise exc.Timeout
            
            elif response.status == 200:
                return json.loads(await response.text())

            elif response.status == 404:
                raise exc.NotFound
                
            elif response.status in [500,502,503,504]:
                raise exc.ServerError
                
            elif response.status == 429:
                raise exc.RateLimit(response.headers)
                
            elif response.status == 403:
                raise exc.Forbidden
                
            elif response.status == 401:
                raise exc.Unauthorized
                
            elif response.status == 400:
                raise exc.BadRequest
                
            else:
                raise Exception("Unidentified error code : "+str(response.status))
            
        return _exceptions
        
    async def fetch(self, url):
        """
        Returns the result of the request of the url given in parameter after attaching the api_key to the header
        """
        async with aiohttp.ClientSession() as session:
            headers = {
                "X-Riot-Token": self._key
            }
            
            try:
                response = await session.request('GET', url, headers=headers)
            #In case of timeout
            except Exception as e:
                return None
            
            #If a logging function is passed, send it url, status code and headers
            if self.requestsLoggingFunction:
                self.requestsLoggingFunction(url, response.status, response.headers)
            
            #await response.text() needed here in the client session, dunno why
            await response.text()
            return response
    
    #Champion mastery
    @errorHandler
    @exceptions
    @ratelimit
    async def getChampionMasteries(self, summonerId):
        """
        :param int summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#champion-mastery-v4/GET_getAllChampionMasteries
        """
        return await self.fetch((self.BASE_URL + "champion-mastery/v4/champion-masteries/by-summoner/{summonerId}").format(server=self._server, summonerId=summonerId))
    
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getChampionMasteriesByChampionId(self, summonerId, championId):
        """
            :param int summonerId: summonerId of the player
            :param int championId: id of the champion

            Returns the result of https://developer.riotgames.com/api-methods/#champion-mastery-v4/GET_getChampionMastery
        """
        return await self.fetch((self.BASE_URL + "champion-mastery/v4/champion-masteries/by-summoner/{summonerId}/by-champion/{championId}").format(server=self._server, summonerId=summonerId, championId=championId))
    
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getChampionMasteriesScore(self, summonerId):
        """
        :param int summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#champion-mastery-v4/GET_getChampionMasteryScore
        """
        return await self.fetch((self.BASE_URL + "champion-mastery/v4/scores/by-summoner/{summonerId}").format(server=self._server, summonerId=summonerId))
    
    
    #Champions
    @errorHandler
    @exceptions
    @ratelimit
    async def getChampionRotations(self):
        """
        Returns the result of https://developer.riotgames.com/api-methods/#champion-v3/GET_getChampionInfo
        """
        return await self.fetch((self.BASE_URL + "platform/v3/champion-rotations").format(server=self._server))
    
    
    #League
    @errorHandler
    @exceptions
    @ratelimit
    async def getLeagueById(self, leagueId):
        """
        :param string leagueId: id of the league
        
        Returns the result of https://developer.riotgames.com/api-methods/#league-v4/GET_getLeagueById
        """
        return await self.fetch((self.BASE_URL + "league/v4/leagues/{leagueId}").format(server=self._server, leagueId=leagueId))
    
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getLeaguePosition(self, summonerId):
        """
        :param int summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#league-v4/GET_getAllLeaguePositionsForSummoner
        """
        return await self.fetch((self.BASE_URL + "league/v4/positions/by-summoner/{summonerId}").format(server=self._server, summonerId=summonerId))
    
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getChallengerLeague(self, queue="RANKED_SOLO_5x5"):
        """
        :param string queue: queue to get the challenger league of
            Values accepted : 
             * RANKED_SOLO_5x5 *(default)*
             * RANKED_FLEX_SR
             * RANKED_FLEX_TT
        
        Returns the result of https://developer.riotgames.com/api-methods/#league-v4/GET_getChallengerLeague
        """
        return await self.fetch((self.BASE_URL + "league/v4/challengerleagues/by-queue/{queue}").format(server=self._server, queue=queue))
    
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getMasterLeague(self, queue="RANKED_SOLO_5x5"):
        """
        :param string queue: queue to get the master league of
            Values accepted : 
             * RANKED_SOLO_5x5 *(default)*
             * RANKED_FLEX_SR
             * RANKED_FLEX_TT
        
        Returns the result of https://developer.riotgames.com/api-methods/#league-v4/GET_getMasterLeague
        """
        return await self.fetch((self.BASE_URL + "league/v4/masterleagues/by-queue/{queue}").format(server=self._server, queue=queue))
    
    
    #Status
    @errorHandler
    @exceptions
    @ratelimit
    async def getStatus(self):
        """
        Returns the result of https://developer.riotgames.com/api-methods/#lol-status-v3/GET_getShardData
        """
        return await self.fetch((self.BASE_URL + "status/v3/shard-data").format(server=self._server))
    
    
    #Match
    @errorHandler
    @exceptions
    @ratelimit
    async def getMatch(self, matchId):
        """
        :param int matchId: matchId of the match, also known as gameId
        
        Returns the result of https://developer.riotgames.com/api-methods/#match-v4/GET_getMatch
        """
        return await self.fetch((self.BASE_URL + "match/v4/matches/{matchId}").format(server=self._server, matchId=matchId))
        
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getTimeline(self, matchId):
        """
        :param int matchId: matchId of the match, also known as gameId
        
        Returns the result of https://developer.riotgames.com/api-methods/#match-v4/GET_getMatchTimeline
        """
        return await self.fetch((self.BASE_URL + "match/v4/timelines/by-match/{matchId}").format(server=self._server, matchId=matchId))
    
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getMatchlist(self, accountId, params=None):
        """
        :param int accountId: accountId of the player
        :param object params: all key:value params to add to the request
        
        Returns the result of https://developer.riotgames.com/api-methods/#match-v4/GET_getMatchlist
        """
        return await self.fetch((self.BASE_URL + "match/v4/matchlists/by-account/{accountId}{params}").format(server=self._server, accountId=accountId, params = utils.urlParams(params)))
    
    
    #Spectator
    @errorHandler
    @exceptions
    @ratelimit
    async def getCurrentGame(self, summonerId):
        """
        :param int summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#spectator-v4/GET_getCurrentGameInfoBySummoner
        """
        return await self.fetch((self.BASE_URL + "spectator/v4/active-games/by-summoner/{summonerId}").format(server=self._server, summonerId=summonerId))
    
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getFeaturedGame(self):
        """
        Returns the result of https://developer.riotgames.com/api-methods/#spectator-v3/GET_getFeaturedGames
        """
        return await self.fetch((self.BASE_URL + "spectator/v3/featured-games").format(server=self._server, summonerId=summonerId))
    
    
    #Summoner
    @errorHandler
    @exceptions
    @ratelimit
    async def getSummoner(self, summonerId):
        """
        :param int summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#summoner-v4/GET_getBySummonerId
        """
        return await self.fetch((self.BASE_URL + "summoner/v4/summoners/{summonerId}").format(server=self._server, summonerId=summonerId))
    
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getSummonerByAccountId(self, accountId):
        """
        :param int accountId: accountId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#summoner-v4/GET_getByAccountId
        """
        return await self.fetch((self.BASE_URL + "summoner/v4/summoners/by-account/{accountId}").format(server=self._server, accountId=accountId))
    
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getSummonerByName(self, summonerName):
        """
        :param string summonerName: name of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#summoner-v4/GET_getBySummonerName
        """
        return await self.fetch((self.BASE_URL + "summoner/v4/summoners/by-name/{summonerName}").format(server=self._server, summonerName=summonerName))
    
    
    #Thirs Party Code
    @errorHandler
    @exceptions
    @ratelimit
    async def getThirdPartyCode(self, summonerId):
        """
        :param int summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#third-party-code-v4/GET_getThirdPartyCodeBySummonerId
        """
        return await self.fetch((self.BASE_URL + "platform/v4/third-party-code/by-summoner/{summonerId}").format(server=self._server, summonerId=summonerId))
    
    