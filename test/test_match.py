from .config import *

def test_match():
    try:
        data = loop.run_until_complete(panth.get_match(matchId))
    except Exception as e:
        print(e)
    
    assert data["metadata"]["matchId"] == matchId
    assert "participants" in data["info"]

    
def test_timeline():
    try:
        data = loop.run_until_complete(panth.get_timeline(matchId))
    except Exception as e:
        print(e)
    
    assert "frames" in data["info"]
    

def test_matchlist():
    try:
        data = loop.run_until_complete(panth.get_matchlist(puuId))
    except exc.NotFound as e:
        pytest.skip("no match found")
    except Exception as e:
        print(e)
    
    assert type(data) == list
    

def test_matchlist_params():
    try:
        data = loop.run_until_complete(panth.get_matchlist(puuId, {"queue":420}))
    except exc.NotFound as e:
        pytest.skip("no match found")
    except Exception as e:
        print(e)
    
    assert type(data) == list
    

def test_matchlist_params_multi():
    try:
        data = loop.run_until_complete(panth.get_matchlist(puuId, {"queue":900, "start":10}))
    except exc.NotFound as e:
        pytest.skip("no match found")
    except Exception as e:
        print(e)
    
    assert type(data) == list
    