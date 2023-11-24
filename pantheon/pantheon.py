import asyncio
import aiohttp
import ssl
import certifi
import json
from functools import wraps

from .utils import utils as utils
from .utils import exceptions as exc

from .RateLimit.RateLimiterManager import RateLimiterManager

class Pantheon():
    
    BASE_URL = "https://{server}.api.riotgames.com/"
    BASE_URL_LOL = BASE_URL + "lol/"
    BASE_URL_TFT = BASE_URL + "tft/"
    BASE_URL_LOR = BASE_URL + "lor/"
    BASE_URL_RIOT = BASE_URL + "riot/"
    BASE_URL_VAL = BASE_URL + "val/"
    
    PLATFORMS = ["br1","eun1","euw1","jp1","kr","la1","la2","na1","oc1","tr1","ru"]
    REGIONS = ["americas","asia","europe", "esports","ap","br","eu","kr","latam","na"]
    PLATFORMS_TO_REGIONS = {"br1":"americas","eun1":"europe","euw1":"europe","jp1":"asia","kr":"asia","la1":"americas","la2":"americas","na1":"americas","oc1":"americas","tr1":"europe","ru":"europe"}
    TOURNAMENT_REGION = "americas"
    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
    
    
    def __init__(self, server, api_key, auto_retry = False, requests_logging_function = None, debug=False):
        """
        Initialize an instance of Pantheon class
        
        :param string server: The server Pantheon will target for the requests. An instance is intended to only call one server. Use multiple instances of Pantheon to call multiples servers.
        It can take the values described there : https://developer.riotgames.com/regional-endpoints.html (euw1, na1...)
        :param string api_key: The API key needed to call the Riot API
        :param boolean auto_retry: Precise if Pantheon should automatically retry after a ratelimit (429) or server error (5XX). Default is False
        :param boolean debug: Allows to print debug messages. Default is False
        """
        self._key = api_key
        self._rl = RateLimiterManager(debug)
        
        self.set_server(server)
        
        self._auto_retry = auto_retry
        self._requests_logging_function = requests_logging_function
        self._debug = debug
        
    def __str__(self):
        return str(self._rl.on(self._platform))
    
    def set_server(self, server):
        if server in self.PLATFORMS:
            self.set_platform(server)
        elif server in self.REGIONS:
            self.set_region(server)
        else:
            raise exc.InvalidServer(server, self.PLATFORMS + self.REGIONS)
    
    def set_platform(self, platform):
        if platform in self.PLATFORMS:
            self._platform = platform
            self._region = self.PLATFORMS_TO_REGIONS[platform]
        else:
            raise exc.InvalidServer(platform, self.PLATFORMS)
            
    def set_region(self, region):
        if region in self.REGIONS:
            self._platform = None
            self._region = region
        else:
            raise exc.InvalidServer(region, self.REGIONS)
    
    
    def locked(self, server):
        """
        Return True if at least one limiter is locked
        """
        return self._rl.on(server).locked()

    def ratelimit_platform(func):
        """
        Decorator for rate limiting at platform level.
        It will handle the operations needed by the RateLimiterManager to ensure the rate limiting and the change of limits considering the returned header.
        """
        @wraps(func)
        async def waitLimit(*args, **params):
            rl = args[0]._rl.on(args[0]._platform)
            token = await rl.getToken(func.__name__)
            
            response = await func(*args, **params)
            
            try:
                limits = utils.getLimits(response.headers)
                timestamp = utils.getTimestamp(response.headers)
            except:
                limits = None
                timestamp = utils.getTimestamp(None)
            
            await rl.getBack(func.__name__, token, timestamp, limits)
            
            return response
            
        return waitLimit

    def ratelimit_region(func):
        """
        Decorator for rate limiting at region level.
        It will handle the operations needed by the RateLimiterManager to ensure the rate limiting and the change of limits considering the returned header.
        """
        @wraps(func)
        async def waitLimit(*args, **params):
            rl = args[0]._rl.on(args[0]._region)
            token = await rl.getToken(func.__name__)
            
            response = await func(*args, **params)
            
            try:
                limits = utils.getLimits(response.headers)
                timestamp = utils.getTimestamp(response.headers)
            except:
                limits = None
                timestamp = utils.getTimestamp(None)
            
            await rl.getBack(func.__name__, token, timestamp, limits)
            
            return response
            
        return waitLimit

    def ratelimit_tournament(func):
        """
        Decorator for rate limiting for tournaments.
        It will handle the operations needed by the RateLimiterManager to ensure the rate limiting and the change of limits considering the returned header.
        """
        @wraps(func)
        async def waitLimit(*args, **params):
            rl = args[0]._rl.on(args[0].TOURNAMENT_REGION)
            token = await rl.getToken(func.__name__)
            
            response = await func(*args, **params)
            
            try:
                limits = utils.getLimits(response.headers)
                timestamp = utils.getTimestamp(response.headers)
            except:
                limits = None
                timestamp = utils.getTimestamp(None)
            
            await rl.getBack(func.__name__, token, timestamp, limits)
            
            return response
            
        return waitLimit
    
    def auto_retry(func):
        """
        Decorator for handling some errors and retrying if needed.
        """
        @wraps(func)
        async def _auto_retry(*args, **params):
            """
            Error handling function for decorator
            """
            if not args[0]._auto_retry:
                return await func(*args, **params)
            else:
                try:
                    return await func(*args, **params)
                #Errors that should be retried
                except exc.RateLimit as e:
                    if args[0]._debug:
                        print(e)
                        print("Retrying")
                    i = e.waitFor()
                    while i < 6:
                        await asyncio.sleep(i)
                        try:
                            return await func(*args, **params)
                        except Exception as e2:
                            if args[0]._debug:
                                print(e2)
                        i += 2
                    raise e
                except (exc.ServerError, exc.Timeout) as e:
                    if args[0]._debug:
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
                        if args[0]._debug:
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
                
        return _auto_retry
    
    def exceptions(func):
        """
        Decorator translating status code into exceptions
        """
        @wraps(func)
        async def _exceptions(*args, **params):
            
            response = await func(*args, **params)
            
            if response is None:
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
                
            elif response.status == 408:
                raise exc.Timeout
                
            else:
                raise Exception("Unidentified error code : "+str(response.status))
            
        return _exceptions
        
    async def fetch(self, url, method="GET", data=None):
        """
        Returns the result of the request of the url given in parameter after attaching the api_key to the header
        """
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "X-Riot-Token": self._key
            }
            
            try:
                if method=="GET":
                    response = await session.request("GET", url, headers=headers, ssl=self.SSL_CONTEXT)
                else:
                    response = await session.request(method, url, headers=headers, data=json.dumps(data), ssl=self.SSL_CONTEXT)
            #In case of timeout
            except Exception as e:
                print(e)
                return None
            
            #If a logging function is passed, send it url, status code and headers
            if self._requests_logging_function:
                self._requests_logging_function(url, response.status, response.headers)
            
            #await response.text() needed here in the client session, dunno why
            await response.text()
            return response
    
    #Champion mastery
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_champion_masteries(self, summonerId):
        """
        :param string summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#champion-mastery-v4/GET_getAllChampionMasteries
        """
        return await self.fetch((self.BASE_URL_LOL + "champion-mastery/v4/champion-masteries/by-summoner/{summonerId}").format(server=self._platform, summonerId=summonerId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_champion_masteries_by_championId(self, summonerId, championId):
        """
            :param string summonerId: summonerId of the player
            :param int championId: id of the champion

            Returns the result of https://developer.riotgames.com/api-methods/#champion-mastery-v4/GET_getChampionMastery
        """
        return await self.fetch((self.BASE_URL_LOL + "champion-mastery/v4/champion-masteries/by-summoner/{summonerId}/by-champion/{championId}").format(server=self._platform, summonerId=summonerId, championId=championId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_champion_masteries_score(self, summonerId):
        """
        :param string summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#champion-mastery-v4/GET_getChampionMasteryScore
        """
        return await self.fetch((self.BASE_URL_LOL + "champion-mastery/v4/scores/by-summoner/{summonerId}").format(server=self._platform, summonerId=summonerId))
    
    
    #Champions
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_champion_rotations(self):
        """
        Returns the result of https://developer.riotgames.com/api-methods/#champion-v3/GET_getChampionInfo
        """
        return await self.fetch((self.BASE_URL_LOL + "platform/v3/champion-rotations").format(server=self._platform))
    
    
    #League
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_league_by_id(self, leagueId):
        """
        :param string leagueId: id of the league
        
        Returns the result of https://developer.riotgames.com/api-methods/#league-v4/GET_getLeagueById
        """
        return await self.fetch((self.BASE_URL_LOL + "league/v4/leagues/{leagueId}").format(server=self._platform, leagueId=leagueId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_league_pages(self, queue="RANKED_SOLO_5x5", tier="DIAMOND", division="I", page=1):
        """
        :param string queue: queue to get the page of
        :param string tier: tier to get the page of
        :param string division: division to get the page of
        :param int page: page to get
        
        Returns the result of https://developer.riotgames.com/api-methods/#league-v4/GET_getLeagueEntriesForSummoner
        """
        
        return await self.fetch((self.BASE_URL_LOL + "league/v4/entries/{queue}/{tier}/{division}?page={page}").format(server=self._platform, queue=queue, tier=tier, division=division, page=page))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_league_position(self, summonerId):
        """
        :param string summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#league-v4/GET_getLeagueEntriesForSummoner
        """
        return await self.fetch((self.BASE_URL_LOL + "league/v4/entries/by-summoner/{summonerId}").format(server=self._platform, summonerId=summonerId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_challenger_league(self, queue="RANKED_SOLO_5x5"):
        """
        :param string queue: queue to get the challenger league of
            Values accepted : 
             * RANKED_SOLO_5x5 *(default)*
             * RANKED_FLEX_SR
             * RANKED_FLEX_TT
        
        Returns the result of https://developer.riotgames.com/api-methods/#league-v4/GET_getChallengerLeague
        """
        return await self.fetch((self.BASE_URL_LOL + "league/v4/challengerleagues/by-queue/{queue}").format(server=self._platform, queue=queue))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_grandmaster_league(self, queue="RANKED_SOLO_5x5"):
        """
        :param string queue: queue to get the master league of
            Values accepted : 
             * RANKED_SOLO_5x5 *(default)*
             * RANKED_FLEX_SR
             * RANKED_FLEX_TT
        
        Returns the result of https://developer.riotgames.com/api-methods/#league-v4/GET_getGrandmasterLeague
        """
        return await self.fetch((self.BASE_URL_LOL + "league/v4/grandmasterleagues/by-queue/{queue}").format(server=self._platform, queue=queue))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_master_league(self, queue="RANKED_SOLO_5x5"):
        """
        :param string queue: queue to get the master league of
            Values accepted : 
             * RANKED_SOLO_5x5 *(default)*
             * RANKED_FLEX_SR
             * RANKED_FLEX_TT
        
        Returns the result of https://developer.riotgames.com/api-methods/#league-v4/GET_getMasterLeague
        """
        return await self.fetch((self.BASE_URL_LOL + "league/v4/masterleagues/by-queue/{queue}").format(server=self._platform, queue=queue))
    
    
    #Status
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_status(self):
        """
        Returns the result of https://developer.riotgames.com/apis#lol-status-v4/GET_getPlatformData
        """
        return await self.fetch((self.BASE_URL_LOL + "status/v4/platform-data").format(server=self._platform))
    
    
    #Match
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_match(self, matchId):
        """
        :param int matchId: matchId of the match, also known as gameId
        
        Returns the result of https://developer.riotgames.com/apis#match-v5/GET_getMatch
        """
        return await self.fetch((self.BASE_URL_LOL + "match/v5/matches/{matchId}").format(server=self._region, matchId=matchId))
        
    
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_timeline(self, matchId):
        """
        :param int matchId: matchId of the match, also known as gameId
        
        Returns the result of https://developer.riotgames.com/apis#match-v5/GET_getTimeline
        """
        return await self.fetch((self.BASE_URL_LOL + "match/v5/matches/{matchId}/timeline").format(server=self._region, matchId=matchId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_matchlist(self, puuId, params=None):
        """
        :param string puuId: puuId of the player
        :param object params: all key:value params to add to the request
        
        Returns the result of https://developer.riotgames.com/apis#match-v5/GET_getMatchIdsByPUUID
        """
        return await self.fetch((self.BASE_URL_LOL + "match/v5/matches/by-puuid/{puuId}/ids{params}").format(server=self._region, puuId=puuId, params = utils.urlParams(params)))

    #Spectator
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_current_game(self, summonerId):
        """
        :param string summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#spectator-v4/GET_getCurrentGameInfoBySummoner
        """
        return await self.fetch((self.BASE_URL_LOL + "spectator/v4/active-games/by-summoner/{summonerId}").format(server=self._platform, summonerId=summonerId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_featured_games(self):
        """
        Returns the result of https://developer.riotgames.com/api-methods/#spectator-v3/GET_getFeaturedGames
        """
        return await self.fetch((self.BASE_URL_LOL + "spectator/v4/featured-games").format(server=self._platform))
    
    
    #Summoner
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_summoner(self, summonerId):
        """
        :param string summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#summoner-v4/GET_getBySummonerId
        """
        return await self.fetch((self.BASE_URL_LOL + "summoner/v4/summoners/{summonerId}").format(server=self._platform, summonerId=summonerId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_summoner_by_accountId(self, accountId):
        """
        :param string accountId: accountId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#summoner-v4/GET_getByAccountId
        """
        return await self.fetch((self.BASE_URL_LOL + "summoner/v4/summoners/by-account/{accountId}").format(server=self._platform, accountId=accountId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_summoner_by_name(self, summonerName):
        """
        :param string summonerName: name of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#summoner-v4/GET_getBySummonerName
        """
        return await self.fetch((self.BASE_URL_LOL + "summoner/v4/summoners/by-name/{summonerName}").format(server=self._platform, summonerName=summonerName))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_summoner_by_puuId(self, puuId):
        """
        :param string puuId: puuId of the player
        
        Returns the result of https://developer.riotgames.com/apis#summoner-v4/GET_getByPUUID
        """
        return await self.fetch((self.BASE_URL_LOL + "summoner/v4/summoners/by-puuid/{puuId}").format(server=self._platform, puuId=puuId))
    
    
    #Third Party Code
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_third_party_code(self, summonerId):
        """
        :param string summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/api-methods/#third-party-code-v4/GET_getThirdPartyCodeBySummonerId
        """
        return await self.fetch((self.BASE_URL_LOL + "platform/v4/third-party-code/by-summoner/{summonerId}").format(server=self._platform, summonerId=summonerId))
    
    
    #Tournaments
    @auto_retry
    @exceptions
    @ratelimit_tournament
    async def register_provider(self, region, callback_url, stub=False):
        """
        :param str region: region to get a provider for
        :param str callback_url: url to which a callback will be sent after each match created with a tournament code from this provider
        
        Returns the result of https://developer.riotgames.com/api-methods/#tournament-stub-v4/POST_registerProviderData
        """
        return await self.fetch((self.BASE_URL_LOL+"tournament{stub}/v4/providers").format(server=self.TOURNAMENT_REGION, stub="-stub" if stub else ""), method="POST", data={"region":region, "url":callback_url})
    
    
    @auto_retry
    @exceptions
    @ratelimit_tournament
    async def register_tournament(self, providerId, name, stub=False):
        """
        :param int providerId: providerId to create a tournament
        :param str name: name of the tournament
        
        Returns the result of https://developer.riotgames.com/api-methods/#tournament-stub-v4/POST_registerTournament
        """
        return await self.fetch((self.BASE_URL_LOL+"tournament{stub}/v4/tournaments").format(server=self.TOURNAMENT_REGION, stub="-stub" if stub else ""), method="POST", data={"providerId":providerId, "name":name})
    
    
    @auto_retry
    @exceptions
    @ratelimit_tournament
    async def create_tournament_code(self, tournamentId, data, nb_codes=1, stub=False):
        """
        :param int tournamentId: tournamentId for which the code will be created
        :param int nb_codes: number of codes to generate
        :param dict data: datafor the code generation, including : 
            list[str] allowedSummonerIds: list of all summonerId (optional)
            str mapType: map for the game
            str pickType: pick type for the game
            str spectatorType: spectator type for the game
            int teamSize: max number of player in a team
            str metadata: additional data to get back with the callback (optional)
        
        Returns the result of https://developer.riotgames.com/api-methods/#tournament-stub-v4/POST_createTournamentCode
        """
        return await self.fetch((self.BASE_URL_LOL+"tournament{stub}/v4/codes?count={nb_codes}&tournamentId={tournamentId}").format(server=self.TOURNAMENT_REGION, stub="-stub" if stub else "", tournamentId=tournamentId, nb_codes=nb_codes), method="POST", data=data)
    
    
    @auto_retry
    @exceptions
    @ratelimit_tournament
    async def get_lobby_events(self, tournamentCode, stub=False):
        """
        :param int providerId: providerId to create a tournament
        :param str name: name of the tournament
        
        Returns the result of https://developer.riotgames.com/api-methods/#tournament-stub-v4/GET_getLobbyEventsByCode
        """
        return await self.fetch((self.BASE_URL_LOL+"tournament{stub}/v4/lobby-events/by-code/{code}").format(server=self.TOURNAMENT_REGION, stub="-stub" if stub else "", code=tournamentCode))
    
    
    # Clash
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_clash_tournaments(self):
        """        
        Returns the result of https://developer.riotgames.com/apis#clash-v1/GET_getTournaments
        """
        return await self.fetch((self.BASE_URL_LOL + "clash/v1/tournaments").format(server=self._platform))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_clash_tournament_by_id(self, tournamentId):
        """
        :param int tournamentId: id of the tournament
        
        Returns the result of https://developer.riotgames.com/apis#clash-v1/GET_getTournamentById
        """
        return await self.fetch((self.BASE_URL_LOL + "clash/v1/tournaments/{tournamentId}").format(server=self._platform, tournamentId=tournamentId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_clash_tournament_by_teamId(self, teamId):
        """
        :param string teamId: id of the team
        
        Returns the result of https://developer.riotgames.com/apis#clash-v1/GET_getTournamentByTeam
        """
        return await self.fetch((self.BASE_URL_LOL + "clash/v1/tournaments/by-team/{teamId}").format(server=self._platform, teamId=teamId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_clash_team_by_id(self, teamId):
        """
        :param string teamId: id of the team
        
        Returns the result of https://developer.riotgames.com/apis#clash-v1/GET_getTeamById
        """
        return await self.fetch((self.BASE_URL_LOL + "clash/v1/teams/{teamId}").format(server=self._platform, teamId=teamId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_clash_players_by_summonerId(self, summonerId):
        """
        :param string summonerId: id of the summoner
        
        Returns the result of https://developer.riotgames.com/apis#clash-v1/GET_getPlayersBySummoner
        """
        return await self.fetch((self.BASE_URL_LOL + "clash/v1/players/by-summoner/{summonerId}").format(server=self._platform, summonerId=summonerId))
    
    
    
    # TFT
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_tft_league_by_id(self, leagueId):
        """
        :param string leagueId: id of the league
        
        Returns the result of https://developer.riotgames.com/apis#tft-league-v1/GET_getLeagueById
        """
        return await self.fetch((self.BASE_URL_TFT + "league/v1/leagues/{leagueId}").format(server=self._platform, leagueId=leagueId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_tft_league_pages(self,  tier="DIAMOND", division="I", page=1):
        """
        :param string tier: tier to get the page of
        :param string division: division to get the page of
        :param int page: page to get
        
        Returns the result of https://developer.riotgames.com/apis#tft-league-v1/GET_getLeagueEntries
        """
        return await self.fetch((self.BASE_URL_TFT + "league/v1/entries/{tier}/{division}?page={page}").format(server=self._platform, tier=tier, division=division, page=page))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_tft_league_position(self, summonerId):
        """
        :param string summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/apis#tft-league-v1/GET_getLeagueEntriesForSummoner
        """
        return await self.fetch((self.BASE_URL_TFT + "league/v1/entries/by-summoner/{summonerId}").format(server=self._platform, summonerId=summonerId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_tft_challenger_league(self):
        """
        Returns the result of https://developer.riotgames.com/apis#tft-league-v1/GET_getChallengerLeague
        """
        return await self.fetch((self.BASE_URL_TFT + "league/v1/challenger").format(server=self._platform))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_tft_grandmaster_league(self):
        """
        Returns the result of https://developer.riotgames.com/apis#tft-league-v1/GET_getGrandmasterLeague
        """
        return await self.fetch((self.BASE_URL_TFT + "league/v1/grandmaster").format(server=self._platform))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_tft_master_league(self):
        """
        Returns the result of https://developer.riotgames.com/apis#tft-league-v1/GET_getMasterLeague
        """
        return await self.fetch((self.BASE_URL_TFT + "league/v1/master").format(server=self._platform))
    
    
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_tft_match(self, matchId):
        """
        :param string matchId: matchId of the match, also known as gameId
        
        Returns the result of https://developer.riotgames.com/api-methods/#match-v4/GET_getMatch
        """
        return await self.fetch((self.BASE_URL_TFT + "match/v1/matches/{matchId}").format(server=self._region, matchId=matchId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_tft_matchlist(self, puuId, params=None):
        """
        :param string puuId: puuId of the player
        :param object params: all key:value params to add to the request
        
        Returns the result of https://developer.riotgames.com/apis#tft-match-v1/GET_getMatchIdsByPUUID
        """
        return await self.fetch((self.BASE_URL_TFT + "match/v1/matches/by-puuid/{puuId}/ids{params}").format(server=self._region, puuId=puuId, params = utils.urlParams(params)))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_tft_summoner(self, summonerId):
        """
        :param string summonerId: summonerId of the player
        
        Returns the result of https://developer.riotgames.com/apis#tft-summoner-v1/GET_getBySummonerId
        """
        return await self.fetch((self.BASE_URL_TFT + "summoner/v1/summoners/{summonerId}").format(server=self._platform, summonerId=summonerId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_tft_summoner_by_accountId(self, accountId):
        """
        :param string accountId: accountId of the player
        
        Returns the result of https://developer.riotgames.com/apis#tft-summoner-v1/GET_getByAccountId
        """
        return await self.fetch((self.BASE_URL_TFT + "summoner/v1/summoners/by-account/{accountId}").format(server=self._platform, accountId=accountId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_tft_summoner_by_puuId(self, puuId):
        """
        :param string puuId: puuId of the player
        
        Returns the result of https://developer.riotgames.com/apis#tft-summoner-v1/GET_getByPUUID
        """
        return await self.fetch((self.BASE_URL_TFT + "summoner/v1/summoners/by-puuid/{puuId}").format(server=self._platform, puuId=puuId))
    
    
    @auto_retry
    @exceptions
    @ratelimit_platform
    async def get_tft_summoner_by_name(self, summonerName):
        """
        :param string summonerName: name of the player
        
        Returns the result of https://developer.riotgames.com/apis#tft-summoner-v1/GET_getBySummonerName
        """
        return await self.fetch((self.BASE_URL_TFT + "summoner/v1/summoners/by-name/{summonerName}").format(server=self._platform, summonerName=summonerName))
    
    
    
    # Riot (general account endpoints)
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_account_by_puuId(self, puuId):
        """
        :param string puuId: puuId of the player
        
        Returns the result of https://developer.riotgames.com/apis#account-v1/GET_getByPuuid
        """
        return await self.fetch((self.BASE_URL_RIOT + "account/v1/accounts/by-puuid/{puuId}").format(server=self._region, puuId=puuId))
    
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_account_by_riotId(self, gameName, tagLine):
        """
        :param string gameName: name of the player
        :param string tagLine: tag of the player
        
        Returns the result of https://developer.riotgames.com/apis#account-v1/GET_getByRiotId
        """
        return await self.fetch((self.BASE_URL_RIOT + "account/v1/accounts/by-riot-id/{gameName}/{tagLine}").format(server=self._region, gameName=gameName, tagLine=tagLine))
    
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_active_shards(self, puuId, game):
        """
        :param string puuId: puuId of the player
        :param string game: targeted game ("val" or "lor")
        
        Returns the result of https://developer.riotgames.com/apis#account-v1/GET_getActiveShard
        """
        return await self.fetch((self.BASE_URL_RIOT + "account/v1/active-shards/by-game/{game}/by-puuid/{puuId}").format(server=self._region, game=game, puuId=puuId))
    
    
    # LoR
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_lor_leaderboard(self):
        """
        Returns the result of https://developer.riotgames.com/apis#lor-ranked-v1/GET_getLeaderboards
        """
        server = self._region if not self._region == "asia" else "sea"
        return await self.fetch((self.BASE_URL_LOR + "ranked/v1/leaderboards").format(server=server))
    
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_lor_match(self, matchId):
        """
        :param string matchId: matchId of the match, also known as gameId
        Returns the result of https://developer.riotgames.com/apis#lor-match-v1/GET_getMatch
        """
        server = self._region if not self._region == "asia" else "sea"
        return await self.fetch((self.BASE_URL_LOR + "match/v1/matches/{matchId}").format(server=server, matchId=matchId))
    
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_lor_matchlist(self, puuId):
        """
        :param string puuId: puuId of the player
        Returns the result of https://developer.riotgames.com/apis#lor-match-v1/GET_getMatchIdsByPUUID
        """
        server = self._region if not self._region == "asia" else "sea"
        return await self.fetch((self.BASE_URL_LOR + "match/v1/matches/by-puuid/{puuid}/ids").format(server=server, puuid=puuId))
    
    
    # Valorant
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_valorant_content(self, locale=None):
        """
        :param string locale: language return. Default to None
        
        Returns the result of https://developer.riotgames.com/apis#val-content-v1/GET_getContent
        """
        return await self.fetch((self.BASE_URL_VAL + "content/v1/contents{locale}").format(server=self._region, locale="?locale="+locale if locale is not None else ""))
    
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_valorant_match(self, matchId):
        """
        :param string matchId: id of the match
        
        Returns the result of https://developer.riotgames.com/apis#val-match-v1/GET_getMatch
        """
        return await self.fetch((self.BASE_URL_VAL + "match/v1/matches/{matchId}").format(server=self._region, matchId=matchId))
    
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_valorant_matchlist(self, puuId):
        """
        :param string puuId: puuId of the player
        
        Returns the result of https://developer.riotgames.com/apis#val-match-v1/GET_getMatchlist
        """
        return await self.fetch((self.BASE_URL_VAL + "match/v1/matchlists/by-puuid/{puuId}").format(server=self._region, puuId=puuId))
    
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_valorant_recent_matches(self, queue):
        """
        :param string queue: queue of the matches
        
        Returns the result of https://developer.riotgames.com/apis#val-match-v1/GET_getRecent
        """
        return await self.fetch((self.BASE_URL_VAL + "match/v1/recent-matches/by-queue/{queue}").format(server=self._region, queue=queue))
    
    @auto_retry
    @exceptions
    @ratelimit_region
    async def get_valorant_leaderboard(self, actId, size=200, startIndex=0):
        """
        :param string actId: id of the act for the leaderboards
        :param int size: size of the leaderboard list
        :param int startIndex: index to start the leaderboard list
        
        Returns the result of https://developer.riotgames.com/apis#val-ranked-v1/GET_getLeaderboard
        """
        return await self.fetch((self.BASE_URL_VAL + "ranked/v1/leaderboards/by-act/{actId}?size={}size&startIndex={startIndex}").format(server=server, size=size, startIndex=startIndex))

    
