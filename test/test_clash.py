from .config import *

def test_getClashTournaments():
    try:
        data = loop.run_until_complete(panth.get_clash_tournaments())
    except Exception as e:
        print(e)
    
    assert type(data) == list
    if len(data) > 0:
        assert "id" in data[0]
        assert "themeId" in data[0]
        assert "schedule" in data[0]

def test_getClashTournamentById():
    try:
        data = loop.run_until_complete(panth.get_clash_tournament_by_id(clash_tournamentId))
    except Exception as e:
        print(e)
    
    assert "id" in data
    assert "themeId" in data
    assert "schedule" in data

def test_getClashTournamentByTeamId():
    try:
        data = loop.run_until_complete(panth.get_clash_tournament_by_teamId(clash_teamId))
    except Exception as e:
        print(e)
    
    assert "id" in data
    assert "themeId" in data
    assert "schedule" in data

def test_getClashTeamById():
    try:
        data = loop.run_until_complete(panth.get_clash_team_by_id(clash_teamId))
    except Exception as e:
        print(e)
    
    assert "id" in data
    assert "tournamentId" in data
    assert "players" in data
        
        
def test_getClashPlayersBySummonerId():
    try:
        data = loop.run_until_complete(panth.get_clash_players_by_summonerId(clash_summonerId))
    except Exception as e:
        print(e)
    
    assert type(data) == list
    if len(data) > 0:
        assert "teamId" in data[0]
        assert "role" in data[0]