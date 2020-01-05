import asyncio
import pytest

from pantheon import pantheon
from pantheon.utils import exceptions as exc

# API details
api_key = "RGAPI-635d8aec-c5a2-4656-a3de-cf6c706e1c92"
server = "euw1"
panth = pantheon.Pantheon(server, api_key, errorHandling=True)

# Summoner details
name = "Canisback"
accountId = "VRTAqAZgHiTwK90Xd9hAaRejrTD0D9n69izLSqQwKf9sug"
summonerId = "Oizbr1dzsLM9ygEADNequ88CIRCq2wDV5EeWcxZQFWSKFvc"
puuid = "hhH5SNlbp-0xYiernub2nxBdMeuNxQRRDcCI4bXh4xoE4bS_II1d-lemvVT3Q2Uf0ZdiJmnr0GOhBg"


# League details
leagueId = "d112cf40-35be-11e9-947f-c81f66db01ef"

## Set to True if skipping apex tiers
too_early = False

# Match details
matchId = 4259542242

# Tournament details
stub = True
tournament_region = "EUW"
tournament_url = "http://test.com"
tournament_name = "Test"

provider_id = 633
tournament_id = 1923
tournament_code = "EUW1923-TOURNAMENTCODE0001"

# TFT details
tft_leagueId = "30032c60-f82a-11e9-8d92-a2a060ae885a"

tft_matchId = "EUW1_4268130192"

loop = asyncio.get_event_loop() 
