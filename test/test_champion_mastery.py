from .config import *


def test_championMastery_by_summonerId():
    try:
        data = loop.run_until_complete(panth.get_champion_masteries(summonerId))
    except Exception as e:
        print(e)
    
    assert type(data) == list
    assert len(data) > 0
    

def test_championMastery_by_summonerId_by_championId():
    try:
        data = loop.run_until_complete(panth.get_champion_masteries_by_championId(summonerId, 89)) # Leona
    except Exception as e:
        print(e)
    
    assert data["championId"] == 89
    assert data["championLevel"] == 7


def test_championMasteryScore_by_summonerId():
    try:
        data = loop.run_until_complete(panth.get_champion_masteries_score(summonerId))
    except Exception as e:
        print(e)
    
    assert type(data) == int
    assert data > 200
    
    