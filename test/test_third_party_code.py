from .config import *

def test_code():
    try:
        data = loop.run_until_complete(panth.get_third_party_code(summonerId))
    except exc.NotFound as e:
        pytest.skip("code not set")
    except Exception as e:
        print(e)
    
    assert type(data) == str