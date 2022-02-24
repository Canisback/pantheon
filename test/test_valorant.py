from .config import *

def test_content():
    try:
        data = loop.run_until_complete(panth_eu.get_valorant_content())
    except exc.ServerError as e:
        pytest.skip("Riot API shitting itself again")
    except Exception as e:
        print(e)
    
    assert "version" in data
    assert "characters" in data
    assert "chromas" in data
    
    assert type(data["characters"]) == list
    assert type(data["chromas"]) == list
    
    
def test_match():
    try:
        data = loop.run_until_complete(panth_eu.get_valorant_match(val_matchId))
    except Exception as e:
        print(e)
    
    assert "matchInfo" in data
    assert "players" in data
    assert "roundResults" in data
    
    assert type(data["players"]) == list
    assert type(data["roundResults"]) == list
    
def test_matchlist():
    try:
        data = loop.run_until_complete(panth_eu.get_valorant_matchlist(val_puuid))
    except Exception as e:
        print(e)
    
    assert "puuid" in data
    assert "history" in data
    
    assert type(data["history"]) == list
    
def test_recent_matchlist():
    try:
        data = loop.run_until_complete(panth_eu.get_valorant_recent_matches("competitive"))
    except Exception as e:
        print(e)
    
    assert type(data["matchIds"]) == list