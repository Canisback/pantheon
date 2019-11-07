from config import *

def test_active_game():
    try:
        data = loop.run_until_complete(panth.getCurrentGame(summonerId))
    except exc.NotFound as e:
        pytest.skip("not currently in game")
    except Exception as e:
        print(e)
    
    assert any([p["summonerId"] == summonerId for p in data["participants"]])
    

def test_featured():
    try:
        data = loop.run_until_complete(panth.getFeaturedGame())
    except Exception as e:
        print(e)
        
    assert type(data["gameList"]) == list
    