from .config import *

def test_leaderboard():
    try:
        data = loop.run_until_complete(panth_americas.getLeaderboard())
    except Exception as e:
        print(e)
    
    assert "players" in data
    
    assert type(data["players"]) == list

def test_match():
    try:
        data = loop.run_until_complete(panth_americas.getLoRMatch(lor_matchId))
    except Exception as e:
        print(e)
    
    assert "metadata" in data
    assert "info" in data
    
def test_matchlist():
    try:
        data = loop.run_until_complete(panth_americas.getLoRMatchlist(lor_puuid))
    except Exception as e:
        print(e)
    
    assert type(data) == list