class NotFound(Exception):
    def __init__(self):
        Exception.__init__(self,"404 Not Found")
        
        
class ServerError(Exception):
    def __init__(self):
        Exception.__init__(self,"Server error, try again later")
        

class RateLimit(Exception):
    def __init__(self, headers):
        print(headers)
        Exception.__init__(self,"Rate limit exceeded")


class Forbidden(Exception):
    def __init__(self):
        Exception.__init__(self,"Access forbidden, your key may be expired or blacklisted. Check the dev portal : https://developer.riotgames.com/")


class Unauthorized(Exception):
    def __init__(self):
        Exception.__init__(self,"Unauthorized, check your API key")


class BadRequest(Exception):
    def __init__(self):
        Exception.__init__(self,"Bad request, the parameters you give might not be handled by the API. Check the API docs : https://developer.riotgames.com/api-methods/")


class Timeout(Exception):
    def __init__(self):
        Exception.__init__(self,"Timeout reached, try again alter")