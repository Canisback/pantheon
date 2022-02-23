from .config import *

def test_tft_match():
    try:
        data = loop.run_until_complete(panth.get_tft_match(tft_matchId))
    except Exception as e:
        print(e)
    
    assert "metadata" in data
    assert "info" in data
    assert data["metadata"]["match_id"] == tft_matchId

    
def test_tft_matchlist():
    try:
        data = loop.run_until_complete(panth.get_tft_matchlist(puuId))
    except exc.NotFound as e:
        pytest.skip("no match found")
    except Exception as e:
        print(e)
    
    assert type(data) == list