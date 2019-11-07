from config import *

def test_champion():
    try:
        data = loop.run_until_complete(panth.getChampionRotations())
    except Exception as e:
        print(e)
    
    assert "freeChampionIds" in data
    assert "freeChampionIdsForNewPlayers" in data
    assert "maxNewPlayerLevel" in data
    
    assert type(data["freeChampionIds"]) == list
    assert type(data["freeChampionIdsForNewPlayers"]) == list
    
    