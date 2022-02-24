import asyncio
import pytest

from pantheon import Pantheon
from pantheon.utils import exceptions as exc

import os

# API details
api_key = os.environ['PANTHEON_KEY']
server = "euw1"
panth = Pantheon(server, api_key, auto_retry=True)

panth_eu = Pantheon("eu", api_key, auto_retry=True)

# Summoner details
name = "Canisback"
tag = "EUW1"
accountId = "mCT1-43iYmFMG0-X2efejgX6JBnMneMnGXALxYTE_1nvaQ"
summonerId = "r3jOCGc0_W5N9lg-ZANlC2CSEnn-7wMGm_hZAdo-bxprB_4"
puuId = "S6OWGeKQqY-SCU8931OPdK2zmenypS5Hs_YHv6SrmBDAVMMJpDQeTq8q06tzTFHvNaXWoIf6Fm5iTg"


# League details
leagueId = "d112cf40-35be-11e9-947f-c81f66db01ef"

## Set to True if skipping apex tiers
too_early = False
too_early_tft = False

# Match details
matchId = "EUW1_5742254354"

# Tournament details
stub = True
tournament_region = "EUW"
tournament_url = "http://test.com"
tournament_name = "Test"

# TFT details
tft_leagueId = "30032c60-f82a-11e9-8d92-a2a060ae885a"

tft_matchId = "EUW1_5742439028"

loop = asyncio.get_event_loop() 

# Clash data
clash_summonerId = "r3jOCGc0_W5N9lg-ZANlC2CSEnn-7wMGm_hZAdo-bxprB_4"
clash_teamId = "1139965"
clash_tournamentId = 2002


#Valorant data
val_puuid = "gN5dQedVxymZGD8atprfa_tIeZyl-rDFT1o23eKWgJ9ndawj8CBK_1P-1Mbi6g6_-XGG6EtWkMS7pQ"
val_matchId = "81df03af-69bd-4ed1-8006-b6286bdb3f0a"

# LoR data
lor_puuid = "2a-I8ATOrJJ7PnqMSR6NQ9BlB6RL7tYhu7ocDuQIZY4WIzr-scvPyTCiSZaW5q9ff2BnrcTbDsa9lw"
lor_matchId = "4f5b6a7d-23ed-4256-9fb6-b2810c3c3b92"