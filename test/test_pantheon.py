from .config import *

def test_pantheon_str(capfd):
    print(panth)
    out, err = capfd.readouterr()
    assert out.startswith("Rate limits :")
    
def test_pantheon_locked():
    assert not panth.locked("euw1")
    

def test_platform_1():
    p = Pantheon("euw1", api_key, auto_retry=True)
    
    assert p._platform == "euw1"
    assert p._region == "europe"
    
def test_platform_2():
    p = Pantheon("europe", api_key, auto_retry=True)
    
    assert p._platform == None
    assert p._region == "europe"
    
def test_singleton():
    p = Pantheon("na1", api_key, auto_retry=True)
    
    assert p._rl == panth._rl