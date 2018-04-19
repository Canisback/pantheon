
import time, datetime

def getLimits(headers):
    if 'X-Method-Rate-Limit' in headers and 'X-App-Rate-Limit' in headers:
        appLimits = {}
        for appLimit in headers['X-App-Rate-Limit'].split(","):
            appLimits[int(appLimit.split(":")[1])] = int(appLimit.split(":")[0])

        methodLimits = {}
        for methodLimit in headers['X-Method-Rate-Limit'].split(","):
            methodLimits[int(methodLimit.split(":")[1])] = int(methodLimit.split(":")[0])

        return (appLimits,methodLimits)
    return None

def dateToTimestamp(date):
    return int(time.mktime(datetime.datetime.strptime(date, '%a, %d %b %Y %H:%M:%S GMT').timetuple()))


def urlParams(params):
    if params == None:
        return ""
    else:
        strParams = "?"
        for i in params:
            strParams+= i+"="+str(params[i])+"&"
        return strParams[:-1]