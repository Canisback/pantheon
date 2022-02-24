from .RateLimiter import RateLimiter
from ..utils.utils import Singleton

class RateLimiterManager(metaclass=Singleton):
    def __init__(self, debug):
        
        PLATFORMS = ["br1","eun1","euw1","jp1","kr","la1", "la2","na1","oc1","tr1","ru"]
        REGIONS = ["americas","asia","europe",                    "esports","ap","br","eu","kr","latam","na"]
        
        self.debug=debug
        
        self._rls = {server:RateLimiterServer(self.debug) for server in PLATFORMS + REGIONS}
        
    def on(self, server):
        return self._rls[server]
    
class RateLimiterServer:
    
    #Default application rate limit
    defaultApplicationLimits = [(20,1),(100,120)]
    
    defaultMethodsLimits = {
        "get_champion_masteries":[(2000,60)],
        "get_champion_masteries_by_championId":[(2000,60)],
        "get_champion_masteries_score":[(2000,60)],
        "get_champion_rotations":[(30,10),(500,600)],
        "get_league_by_id":[(500,10)],
        "get_league_pages":[(50,10)],
        "get_league_position":[(300,60)],
        "get_challenger_league":[(30,10),(500,600)],
        "get_grandmaster_league":[(30,10),(500,600)],
        "get_master_league":[(30,10),(500,600)],
        "get_status":[(20000,10),(1200000,600)],
        "get_match":[(250,10)],
        "get_timeline":[(250,10)],
        "get_matchlist":[(500,10)],
        "get_current_game":[(20000,10),(1200000,600)],
        "get_featured_games":[(20000,10),(1200000,600)],
        "get_summoner":[(2000,60)],
        "get_summoner_by_accountId":[(2000,60)],
        "get_summoner_by_name":[(2000,60)],
        "get_summoner_by_puuId":[(2000,60)],
        "get_third_party_code":[(500,60)],
        "register_provider":[(10,10),(500,600)],
        "register_tournament":[(30,10),(500,600)],
        "create_tournament_code":[(30,10),(500,600)],
        "get_lobby_events":[(30,10),(500,600)],
        "get_clash_tournaments":[(10,60)],
        "get_clash_tournament_by_id":[(10,60)],
        "get_clash_tournament_by_teamId":[(200,60)],
        "get_clash_team_by_id":[(200,60)],
        "get_clash_players_by_summonerId":[(200,60)],
        "get_tft_league_by_id":[(100,10)],
        "get_tft_league_pages":[(50,10)],
        "get_tft_league_position":[(300,60)],
        "get_tft_challenger_league":[(30,10),(500,600)],
        "get_tft_grandmaster_league":[(30,10),(500,600)],
        "get_tft_master_league":[(30,10),(500,600)],
        "get_tft_match":[(200,10)],
        "get_tft_matchlist":[(400,10)],
        "get_tft_summoner":[(2000,60)],
        "get_tft_summoner_by_accountId":[(2000,60)],
        "get_tft_summoner_by_name":[(2000,60)],
        "get_tft_summoner_by_puuId":[(2000,60)],
        "get_account_by_puuId":[(1000,60)],
        "get_account_by_riotId":[(1000,60)],
        "get_active_shards":[(20000,10),(1200000,600)],
        "get_lor_leaderboard":[(30,10),(500,600)],
        "get_lor_match":[(100,3600)],
        "get_lor_matchlist":[(200,3600)],
        "get_valorant_content":[(60,60)],
        "get_valorant_match":[(60,60)],
        "get_valorant_matchlist":[(120,60)],
        "get_valorant_recent_matches":[(60,60)],
        "get_valorant_leaderboard":[(10,10)]
    }
    
    def __init__(self, debug):
        
        self.debug=debug
        
        self.application = []
        for appLimit in self.defaultApplicationLimits:
            self.application.append(RateLimiter(self.debug,appLimit, "App"))
            
        self.methods = {}
        
        for method in self.defaultMethodsLimits:
            self.methods[method] = []
            for methodLimit in self.defaultMethodsLimits[method]:
                self.methods[method].append(RateLimiter(self.debug,methodLimit, method))
        
    def __str__(self):
        s = "Rate limits : \n"
        for l in self.application:
            s += "\t" + str(l) + "\n"
        for m in self.methods:
            for ml in self.methods[m]:
                s += "\t" + str(ml) + "\n"
        return s
    
    def locked(self):
        return any([l.locked() for l in self.application] + [ml.locked() for m in self.methods for ml in self.methods[m]])
    
    def updateApplicationLimit(self, duration:int, limit:int):
        for appLimit in self.application:
            if duration == appLimit.getDuration():
                appLimit.updateLimit(limit)
                return
        self.application.append(RateLimiter(self.debug,(limit,duration),"App"))
        
    def deleteApplicationLimit(self, duration:int):
        for appLimit in self.application:
            if duration == appLimit.getDuration():
                self.application.remove(appLimit)
                return
    
    def displayApplicationLimit(self):
        for appLimit in self.application:
            print(str(appLimit.getLimit())+" : "+str(appLimit.getDuration()))
            
    
    def displayApplicationLimiters(self):
        for appLimit in self.application:
            appLimit.displayLimiter()
    
    
    def updateMethodsLimit(self, method:str, duration:int, limit:int):
        if method in self.methods:
            for methodLimit in self.methods[method]:
                if duration == methodLimit.getDuration():
                    methodLimit.updateLimit(limit)
                    return
            self.methods[method].append(RateLimiter(self.debug,(limit,duration),method))
        else:
            self.methods[method] = []
            self.methods[method].append(RateLimiter(self.debug,(limit,duration),method))
        
    def deleteMethodsLimit(self, method:str, duration:int):
        for methodLimit in self.methods[method]:
            if duration == methodLimit.getDuration():
                self.methods[method].remove(methodLimit)
                return
            
    async def getBack(self, method:str, token, timestamp:int, limits):
        if limits is None:
            for i,appLimit in enumerate(self.application):
                await appLimit.getBack(token[0][i], timestamp)
            for i,methodLimit in enumerate(self.methods[method]):
                await methodLimit.getBack(token[1][i], timestamp)
        else:
            appLimitsToDelete = []
            methodsLimitsToDelete = []
            
            for i,appLimit in enumerate(self.application):
                if appLimit.getDuration() in limits[0]:
                    await appLimit.getBack(token[0][i], timestamp, limits[0][appLimit.getDuration()])
                    del(limits[0][appLimit.getDuration()])
                else:
                    #If the limit is not in the returned header, consider it out of date hence, queue to delete it
                    appLimitsToDelete.append(appLimit.getDuration())
                    
            #Delete the out of date limits
            for i in appLimitsToDelete:
                self.deleteApplicationLimit(i)
            
            for duration in limits[0]:
                #If the limit exists in the returned header but not in the manager, create it
                self.updateApplicationLimit(duration,limits[0][duration])
                
            
            for i,methodLimit in enumerate(self.methods[method]):
                if methodLimit.getDuration() in limits[1]:
                    await methodLimit.getBack(token[1][i], timestamp, limits[1][methodLimit.getDuration()])
                    del(limits[1][methodLimit.getDuration()])
                else:
                    #If the limit is not in the returned header, consider it out of date hence, queue to delete it
                    methodsLimitsToDelete.append(methodLimit.getDuration())
            
            #Delete the out of date limits
            for i in methodsLimitsToDelete:
                self.deleteMethodsLimit(method, i)
                
            for duration in limits[1]:
                #If the limit exists in the returned header but not in the manager, create it
                self.updateMethodsLimit(method, duration, limits[1][duration])
                for methodLimit in self.methods[method]:
                    if duration == methodLimit.getDuration():
                        methodLimit.count += 1
                        return
                
    
    def displayMethodsLimit(self):
        for method in self.methods:
            print(method)
            for methodLimit in self.methods[method]:
                print(str(methodLimit.getLimit())+" : "+str(methodLimit.getDuration()))
        print()
    
    def displayMethodLimiters(self, method:str):
        for methodLimit in self.methods[method]:
            methodLimit.displayLimiter()
    
    
        
    async def getToken(self, method:str):
        appToken=[]
        methodToken=[]
        for appLimit in self.application:
            appToken.append(await appLimit.getToken())
        
        if not method in self.methods:
            self.updateMethodsLimit(method, 10, 20000)
        
        for methodLimit in self.methods[method]:
            methodToken.append(await methodLimit.getToken())
        return (appToken,methodToken)
            
        