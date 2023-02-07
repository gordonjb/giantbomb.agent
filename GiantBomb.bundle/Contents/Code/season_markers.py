"""
Markers to divide video lists into seasons.

There's no season API, so can't look up the names or divide episodes by season,
so they are hardcoded here.

Seasons are marked by their `first_ep`, the video's GUID.

Seasons can be named, but don't need to be.
"""

SEASONS = {
    # Mass Alex
    "27": [
        {"name": "Mass Effect 1", "first_ep": "2300-13490"},
        {"name": "Mass Effect 2", "first_ep": "2300-13895"},
        {"name": "Mass Effect 3", "first_ep": "2300-15264"},
    ],
    # Metal Gear Scanlon
    "29": [
        {"name": "Metal Gear Solid", "first_ep": "2300-9365"},
        {"name": "Metal Gear Solid 2: Sons of Liberty", "first_ep": "2300-9652"},
        {"name": "Metal Gear Solid 3: Snake Eater", "first_ep": "2300-9975"},
        {"name": "Metal Gear Solid 4: Guns of the Patriots", "first_ep": "2300-10464"},
        {"name": "Metal Gear Solid V: The Phantom Pain", "first_ep": "2300-10615"},
        {"name": "Metal Gear Rising: Revengeance", "first_ep": "2300-11808"},
    ],
    # Run for the Hills
    "110": [
        {"name": "Run for the Hills", "first_ep": "2300-17357"},
        {"name": "Run 2 the Hills", "first_ep": "2300-17655"},
    ],
    # Six Crazy Frights
    "30": [
        {"first_ep": "2300-16197"},
        {"first_ep": "2300-14857"},
        {"first_ep": "2300-13621"},
        {"first_ep": "2300-12544"},
    ],
    # Who's The Big Boss?
    "36": [
        {"name": "Metal Gear", "first_ep": "2300-12798"},
        {"name": "Metal Gear 2", "first_ep": "2300-13086"},
        {"name": "Metal Gear Solid (GBC)", "first_ep": "2300-13458"},
    ],
}
