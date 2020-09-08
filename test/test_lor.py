from .config import *

def test_leaderboard():
    try:
        data = loop.run_until_complete(panth_americas.getLeaderboard())
    except Exception as e:
        print(e)
    
    assert "players" in data
    
    assert type(data["players"]) == list