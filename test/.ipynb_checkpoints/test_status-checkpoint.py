from config import *

def test_status():
    try:
        data = loop.run_until_complete(panth.getStatus())
    except Exception as e:
        print(e)
    
    assert data["region_tag"] == "eu"
    assert data["slug"] == "euw"
    assert type(data["services"]) == list