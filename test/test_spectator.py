from .config import *

def test_active_game():
    try:
        data = loop.run_until_complete(panth.get_current_game(summonerId))
    except exc.NotFound as e:
        pytest.skip("not currently in game")
    except Exception as e:
        print(e)
    
    assert any([p["summonerId"] == summonerId for p in data["participants"]])
    

def test_featured():
    try:
        data = loop.run_until_complete(panth.get_featured_games())
    except Exception as e:
        print(e)
        
    assert type(data["gameList"]) == list
    