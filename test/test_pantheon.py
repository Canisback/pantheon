from .config import *

def test_pantheon_str(capfd):
    print(panth)
    out, err = capfd.readouterr()
    assert out.startswith("Rate limits :")