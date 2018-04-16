# Pantheon

Simple library to use the Riot API with Python Asyncio.

Not complete at the moment, just having what I needed for now.

It has an efficient rate limiting system as well as an error handler that automatically resend request on when needed.

Currently supported requests : 
 * match by matchId -> getMatch(matchId)
 * match timeline by matchId -> getTimeline(matchId)
 * matchlist by accountId (with parameters) -> getMatchlist(self, accountId, params) / params={"queue":420","season":11}
 * league by leagueId -> getLeagueById(leagueId)
 * league position by summonerId -> getLeaguePosition(summonerId)

Further requests supported and documentation (hopefully) incoming
