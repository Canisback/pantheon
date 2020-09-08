from .config import *

def test_account_puuid():
    try:
        data = loop.run_until_complete(panth_americas.getAccountByPuuId(puuid))
    except Exception as e:
        print(e)
    
    assert "puuid" in data
    assert "gameName" in data
    assert "tagLine" in data
    
def test_account_name():
    try:
        data = loop.run_until_complete(panth_americas.getAccountByRiotId(name, tag))
    except Exception as e:
        print(e)
    
    assert "puuid" in data
    assert "gameName" in data
    assert "tagLine" in data
    
def test_account_shards():
    try:
        data = loop.run_until_complete(panth_americas.getActiveShards(puuid, "val"))
    except Exception as e:
        print(e)
    
    assert "puuid" in data
    assert "game" in data
    assert "activeShard" in data