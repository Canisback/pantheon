from config import *

def test_match():
    try:
        data = loop.run_until_complete(panth.getMatch(matchId))
    except Exception as e:
        print(e)
    
    assert data["gameId"] == matchId
    assert "participants" in data

    
def test_timeline():
    try:
        data = loop.run_until_complete(panth.getTimeline(matchId))
    except Exception as e:
        print(e)
    
    assert "frames" in data
    

def test_matchlist():
    try:
        data = loop.run_until_complete(panth.getMatchlist(accountId))
    except exc.NotFound as e:
        pytest.skip("no match found")
    except Exception as e:
        print(e)
    
    assert type(data["matches"]) == list
    

def test_matchlist_params():
    try:
        data = loop.run_until_complete(panth.getMatchlist(accountId, {"queue":420}))
    except exc.NotFound as e:
        pytest.skip("no match found")
    except Exception as e:
        print(e)
    
    assert all([m["queue"] == 420 for m in data["matches"]])
    

def test_matchlist_params_set():
    try:
        data = loop.run_until_complete(panth.getMatchlist(accountId, {"queue":[420,430]}))
    except exc.NotFound as e:
        pytest.skip("no match found")
    except Exception as e:
        print(e)
    
    assert not all([m["queue"] == 420 for m in data["matches"]])
    assert all([m["queue"] == 420 or m["queue"] == 430 for m in data["matches"]])
    

def test_matchlist_params_multi():
    try:
        data = loop.run_until_complete(panth.getMatchlist(accountId, {"queue":420, "champion":89}))
    except exc.NotFound as e:
        pytest.skip("no match found")
    except Exception as e:
        print(e)
    
    assert all([m["queue"] == 420 and m["champion"] == 89 for m in data["matches"]])
    