from dataclasses import dataclass


# instead of having game_time we can just calculate the average ahead of time...
# might be a better idea
@dataclass
class DataClassMatch:
    inhibitor_kills: int
    tower_kills: int
    baron_kills: int
    dragon_kills: int
    assists: int
    kills: int
    deaths: int
    damage_dealt: float
    total_level: int
    total_gold: int
    game_time: float
    won: bool
