from config import *

def test_tft_leagueId():
    try:
        data = loop.run_until_complete(panth.getTFTLeagueById(tft_leagueId))
    except Exception as e:
        print(e)
    
    assert data["leagueId"] == tft_leagueId
    assert type(data["entries"]) == list
    
    
@pytest.mark.skipif(too_early, reason="Too early in the season")
def test_tft_apex_challenger():
    try:
        data = loop.run_until_complete(panth.getTFTChallengerLeague())
    except Exception as e:
        print(e)
    
    assert data["tier"] == "CHALLENGER"
    assert data["queue"] == "RANKED_TFT"
    assert type(data["entries"]) == list
    
    
@pytest.mark.skipif(too_early, reason="Too early in the season")
def test_tft_apex_grandmaster():
    try:
        data = loop.run_until_complete(panth.getTFTGrandmasterLeague())
    except Exception as e:
        print(e)
    
    assert data["tier"] == "GRANDMASTER"
    assert data["queue"] == "RANKED_TFT"
    assert type(data["entries"]) == list
    
    
@pytest.mark.skipif(too_early, reason="Too early in the season")
def test_tft_apex_master():
    try:
        data = loop.run_until_complete(panth.getTFTMasterLeague())
    except Exception as e:
        print(e)
    
    assert data["tier"] == "MASTER"
    assert data["queue"] == "RANKED_TFT"
    assert type(data["entries"]) == list

    
def test_tft_league_entries_by_summonerId():
    try:
        data = loop.run_until_complete(panth.getTFTLeaguePosition(summonerId))
    except Exception as e:
        print(e)
    
    assert type(data) == list
    

def test_tft_league_entries():
    try:
        data = loop.run_until_complete(panth.getTFTLeaguePages())
    except Exception as e:
        print(e)
    
    assert type(data) == list
    
    if len(data) > 0:
        entry = data[0]
        assert entry["queueType"] == "RANKED_TFT"
        assert entry["tier"] == "DIAMOND"
        assert entry["rank"] == "I"
        
    else:
        pytest.skip("not enough player at this rank")
    

def test_tft_league_entries_params():
    try:
        data = loop.run_until_complete(panth.getTFTLeaguePages(tier="SILVER", division="III"))
    except Exception as e:
        print(e)
    
    assert type(data) == list
    
    if len(data) > 0:
        entry = data[0]
        assert entry["queueType"] == "RANKED_TFT"
        assert entry["tier"] == "SILVER"
        assert entry["rank"] == "III"
        
    else:
        pytest.skip("not enough player at this rank")
    

def test_tft_league_entries_pages():
    try:
        data = loop.run_until_complete(panth.getTFTLeaguePages(tier="SILVER", division="III", page=1))
    except Exception as e:
        print(e)
        
    try:
        data_2 = loop.run_until_complete(panth.getTFTLeaguePages(tier="SILVER", division="III", page=2))
    except Exception as e:
        print(e)
    
    assert type(data) == list
    
    if len(data) > 0 and len(data_2) > 0:
        entry = data[0]
        assert entry["queueType"] == "RANKED_TFT"
        assert entry["tier"] == "SILVER"
        assert entry["rank"] == "III"
        
        entry_2 = data_2[0]
        
        assert not entry == entry_2
        
    else:
        pytest.skip("not enough player at this rank")



