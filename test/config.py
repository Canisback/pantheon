import asyncio
import pytest

from pantheon import pantheon
from pantheon.utils import exceptions as exc

import os

# API details
api_key = os.environ['PANTHEON_KEY']
server = "euw1"
panth = pantheon.Pantheon(server, api_key, errorHandling=True)

panth_americas = pantheon.Pantheon("americas", api_key, errorHandling=True)
panth_eu = pantheon.Pantheon("eu", api_key, errorHandling=True)

# Summoner details
name = "Canisback"
tag = "EUW1"
accountId = "mCT1-43iYmFMG0-X2efejgX6JBnMneMnGXALxYTE_1nvaQ"
summonerId = "r3jOCGc0_W5N9lg-ZANlC2CSEnn-7wMGm_hZAdo-bxprB_4"
puuid = "S6OWGeKQqY-SCU8931OPdK2zmenypS5Hs_YHv6SrmBDAVMMJpDQeTq8q06tzTFHvNaXWoIf6Fm5iTg"


# League details
leagueId = "d112cf40-35be-11e9-947f-c81f66db01ef"

## Set to True if skipping apex tiers
too_early = False
too_early_tft = False

# Match details
matchId = 4259542242

# Tournament details
stub = True
tournament_region = "EUW"
tournament_url = "http://test.com"
tournament_name = "Test"

# TFT details
tft_leagueId = "30032c60-f82a-11e9-8d92-a2a060ae885a"

tft_matchId = "NA1_3525864593"

loop = asyncio.get_event_loop() 

# Clash data
clash_summonerId = "r3jOCGc0_W5N9lg-ZANlC2CSEnn-7wMGm_hZAdo-bxprB_4"
clash_teamId = "1139965"
clash_tournamentId = 2002


#Valorant data
val_puuid = "zxzDtQcrVZGz4-p4e_woWLRZb-DOy2dejjYTH-nLrFgGAjHVXR_qHaOLO80l0YqpKQEo-wtbmbn10w"
val_matchId = "1bbaca47-2918-49c5-9b25-caa9d8ea63fa"

# LoR data
lor_puuid = "4Kk3m_zl1MWJf9VKAsvBmIUKO8LZCqNCLaNgJ0DybNyUU3eydu-lzN88L5RLpn8SxQULn2-SsBKa4Q"
lor_matchId = "829c361c-edca-4305-bc2d-c205051b0a5d"