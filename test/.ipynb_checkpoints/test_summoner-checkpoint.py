from config import *

def test_by_summonerId():
    try:
        data = loop.run_until_complete(panth.getSummoner(summonerId))
    except Exception as e:
        print(e)
    
    assert data["name"] == name
    assert data["id"] == summonerId

    
def test_by_summonerName():
    try:
        data = loop.run_until_complete(panth.getSummonerByName(name))
    except Exception as e:
        print(e)
    
    assert data["name"] == name
    assert data["id"] == summonerId

    
def test_by_accountId():
    try:
        data = loop.run_until_complete(panth.getSummonerByAccountId(accountId))
    except Exception as e:
        print(e)
    
    assert data["name"] == name
    assert data["accountId"] == accountId

    
def test_by_puuId():
    try:
        data = loop.run_until_complete(panth.getSummonerByPuuId(puuid))
    except Exception as e:
        print(e)
    
    assert data["name"] == name
    assert data["puuid"] == puuid