from config import *

def test_tft_by_summonerId():
    try:
        data = loop.run_until_complete(panth.getTFTSummoner(summonerId))
    except Exception as e:
        print(e)
    
    assert data["name"] == name
    assert data["id"] == summonerId

    
def test_tft_by_summonerName():
    try:
        data = loop.run_until_complete(panth.getTFTSummonerByName(name))
    except Exception as e:
        print(e)
    
    assert data["name"] == name
    assert data["id"] == summonerId

    
def test_tft_by_accountId():
    try:
        data = loop.run_until_complete(panth.getTFTSummonerByAccountId(accountId))
    except Exception as e:
        print(e)
    
    assert data["name"] == name
    assert data["accountId"] == accountId

    
def test_tft_by_puuId():
    try:
        data = loop.run_until_complete(panth.getTFTSummonerByPuuId(puuid))
    except Exception as e:
        print(e)
    
    assert data["name"] == name
    assert data["puuid"] == puuid