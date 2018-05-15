from .RateLimiter import RateLimiter

class RateLimiterManager:
    
    #Default application rate limit
    defaultApplicationLimits = [(20,1),(100,120)]
    
    defaultMethodsLimits = {
        "getChampions":[(400,60)],
        "getChampionsById":[(400,60)],
        "getLeagueById":[(500,10)],
        "getLeaguePosition":[(35,60)],
        "getChallengerLeague":[(500,10)],
        "getMasterLeague":[(500,10)],
        "getMatch":[(500,10)],
        "getTimeline":[(500,10)],
        "getMatchlist":[(1000,10)],
        "getSummoner":[(600,60)],
        "getSummonerByName":[(600,60)],
        "getSummonerByAccount":[(1000,60)],
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
        if limits == None:
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
                self.updateMethodsLimit(method, duration,limits[1][duration])
    
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
            
        