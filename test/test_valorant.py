from .config import *

def test_content():
    try:
        data = loop.run_until_complete(panth_eu.getValorantContent())
    except Exception as e:
        print(e)
    
    assert "version" in data
    assert "characters" in data
    assert "chromas" in data
    
    assert type(data["characters"]) == list
    assert type(data["chromas"]) == list
    
    
def test_match():
    try:
        data = loop.run_until_complete(panth_eu.getValorantMatch(val_matchId))
    except Exception as e:
        print(e)
    
    assert "matchInfo" in data
    assert "players" in data
    assert "roundResults" in data
    
    assert type(data["players"]) == list
    assert type(data["roundResults"]) == list
    
def test_matchlist():
    try:
        data = loop.run_until_complete(panth_eu.getValorantMatchlist(val_puuid))
    except Exception as e:
        print(e)
    
    assert "puuid" in data
    assert "history" in data
    
    assert type(data["history"]) == list
    
    