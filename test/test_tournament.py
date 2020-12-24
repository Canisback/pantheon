from .config import *


def test_providers():
    try:
        data = loop.run_until_complete(panth.registerProvider(tournament_region, tournament_url, stub))
    except exc.Unauthorized as e:
        pytest.skip("API key unauthorized for tournament")
    except Exception as e:
        print(e)
    
    assert type(data) == int

def test_tournaments():
    try:
        provider_id = loop.run_until_complete(panth.registerProvider(tournament_region, tournament_url, stub))
        data = loop.run_until_complete(panth.registerTournament(provider_id, tournament_name, stub))
    except exc.Unauthorized as e:
        pytest.skip("API key unauthorized for tournament")
    except Exception as e:
        print(e)
    
    assert type(data) == int

    
def test_code():
    data_input = {
        "mapType": "SUMMONERS_RIFT",
        "metadata": "",
        "pickType": "BLIND_PICK",
        "spectatorType": "NONE",
        "teamSize": 5
    }
    try:
        provider_id = loop.run_until_complete(panth.registerProvider(tournament_region, tournament_url, stub))
        tournament_id = loop.run_until_complete(panth.registerTournament(provider_id, tournament_name, stub))
        data = loop.run_until_complete(panth.createTournamentCode(tournament_id, data_input, 1, stub))
    except exc.Unauthorized as e:
        pytest.skip("API key unauthorized for tournament")
    except Exception as e:
        print(e)
    
    assert type(data) == list
    assert len(data) == 1

    
def test_multiple_codes():
    data_input = {
        "mapType": "SUMMONERS_RIFT",
        "metadata": "",
        "pickType": "BLIND_PICK",
        "spectatorType": "NONE",
        "teamSize": 5
    }
    try:
        provider_id = loop.run_until_complete(panth.registerProvider(tournament_region, tournament_url, stub))
        tournament_id = loop.run_until_complete(panth.registerTournament(provider_id, tournament_name, stub))
        data = loop.run_until_complete(panth.createTournamentCode(tournament_id, data_input, 5, stub))
    except exc.Unauthorized as e:
        pytest.skip("API key unauthorized for tournament")
    except Exception as e:
        print(e)
    
    assert type(data) == list
    assert len(data) == 5

    
def test_lobby():
    try:
        provider_id = loop.run_until_complete(panth.registerProvider(tournament_region, tournament_url, stub))
        data = loop.run_until_complete(panth.getLobbyEvents(provider_id, stub))
    except exc.Unauthorized as e:
        pytest.skip("API key unauthorized for tournament")
    except Exception as e:
        print(e)
    
    assert "eventList" in data
    assert type(data["eventList"]) == list