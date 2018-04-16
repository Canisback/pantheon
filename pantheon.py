import asyncio, aiohttp
import json

import utils.utils as utils
import utils.exceptions as exc

import sys

from RateLimit.RateLimiterManager import RateLimiterManager

class Pantheon():
    
    BASE_URL = "https://{server}.api.riotgames.com/lol/"
    
    def __init__(self, server, api_key, errorHandling = False):
        
        self.key = api_key
        self.server = server
        self.rl = RateLimiterManager()
        
        self.rl.updateApplicationLimit(10,3000)
        self.rl.updateApplicationLimit(600,180000)
        
        self.errorHandling = errorHandling

    def ratelimit(func):
        async def waitLimit(*args, **params):
            token = await args[0].rl.getToken(func.__name__)
            
            response = await func(*args, **params)
            
            limits = utils.getLimits(response.headers)
            timestamp = utils.dateToTimestamp(response.headers['Date'])
            
            await args[0].rl.getBack(func.__name__, token, timestamp, limits)
            
            return response
            
        return waitLimit
    
    def errorHandler(func):
        #return func
        async def _errorHandling(*args, **params):
            if not args[0].errorHandling:
                return await func(*args, **params)
            else:
                try:
                    return await func(*args, **params)
                #Errors that should be retried
                except exc.RateLimit as e:
                    print(e)
                    print("Retrying")
                    i = 1
                    while i < 6:
                        await asyncio.sleep(i)
                        print("slept "+str(i))
                        try:
                            return await func(*args, **params)
                        except (exc.RateLimit, exc.ServerError) as e:
                            print(e)
                        i += 2
                    raise e
                except (exc.ServerError, exc.Timeout) as e:
                    #print(e)
                    #print("Retrying")
                    i = 1
                    while i < 6:
                        await asyncio.sleep(i)
                        #print("slept "+str(i))
                        try:
                            return await func(*args, **params)
                        except (exc.Timeout, exc.ServerError) as e:
                            pass
                            #print(e)
                        i += 2
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
        async with aiohttp.ClientSession() as session:
            headers = {
                "X-Riot-Token": self.key
            }
            
            try:
                response = await session.request('GET', url, headers=headers)
            #In case of timeout
            except Exception as e:
                return None
            
            #await response.text() needed here in the client session, dunno why
            await response.text()
            return response
        
    @errorHandler
    @exceptions
    @ratelimit
    async def getMatch(self, matchId):
        return await self.fetch((self.BASE_URL + "match/v3/matches/{matchId}").format(server=self.server, matchId=matchId))
        
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getTimeline(self, matchId):
        return await self.fetch((self.BASE_URL + "match/v3/timelines/by-match/{matchId}").format(server=self.server, matchId=matchId))
    
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getMatchlist(self, accountId, params=None):
        return await self.fetch((self.BASE_URL + "match/v3/matchlists/by-account/{accountId}{params}").format(server=self.server, accountId=accountId, params = utils.urlParams(params)))
    
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getLeagueById(self, leagueId):
        return await self.fetch((self.BASE_URL + "league/v3/leagues/{leagueId}").format(server=self.server, leagueId=leagueId))
    
    
    @errorHandler
    @exceptions
    @ratelimit
    async def getLeaguePosition(self, summonerId):
        return await self.fetch((self.BASE_URL + "league/v3/positions/by-summoner/{summonerId}").format(server=self.server, summonerId=summonerId))
    
    
    