from .config import *

def test_account_puuid():
    try:
        data = loop.run_until_complete(panth.get_account_by_puuId(puuId))
    except Exception as e:
        print(e)
    
    assert "puuid" in data
    assert "gameName" in data
    assert "tagLine" in data
    
def test_account_name():
    try:
        data = loop.run_until_complete(panth.get_account_by_riotId(name, tag))
    except Exception as e:
        print(e)
    
    assert "puuid" in data
    assert "gameName" in data
    assert "tagLine" in data
    
def test_account_shards():
    try:
        data = loop.run_until_complete(panth.get_active_shards(puuId, "val"))
    except Exception as e:
        print(e)
    
    assert "puuid" in data
    assert "game" in data
    assert "activeShard" in data