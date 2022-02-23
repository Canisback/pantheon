from .config import *

def test_status():
    try:
        data = loop.run_until_complete(panth.get_status())
    except Exception as e:
        print(e)
    
    assert data["id"] == "EUW1"
    assert type(data["incidents"]) == list