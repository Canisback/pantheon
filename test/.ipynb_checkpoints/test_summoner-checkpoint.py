from .config import *

def test_by_summonerId():
    try:
        data = loop.run_until_complete(panth.get_summoner(summonerId))
    except Exception as e:
        print(e)
    
    assert data["name"] == name
    assert data["id"] == summonerId

    
def test_by_summonerName():
    try:
        data = loop.run_until_complete(panth.get_summoner_by_name(name))
    except Exception as e:
        print(e)
    
    assert data["name"] == name
    assert data["id"] == summonerId

    
def test_by_accountId():
    try:
        data = loop.run_until_complete(panth.get_summoner_by_accountId(accountId))
    except Exception as e:
        print(e)
    
    assert data["name"] == name
    assert data["accountId"] == accountId

    
def test_by_puuId():
    try:
        data = loop.run_until_complete(panth.get_summoner_by_puuId(puuId))
    except Exception as e:
        print(e)
    
    assert data["name"] == name
    assert data["puuid"] == puuId