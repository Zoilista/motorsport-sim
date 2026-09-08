from dataclasses import dataclass


@dataclass
class Driver:
    name: str
    number: int

    aggression: float = 0.7
    consistency: float = 0.9
    tyre_management: float = 0.8
    braking_skill: float = 0.85

    def __post_init__(self):
        self.aggression = max(0.0, min(1.0, self.aggression))
        self.consistency = max(0.0, min(1.0, self.consistency))
        self.tyre_management = max(0.0, min(1.0, self.tyre_management))
        self.braking_skill = max(0.0, min(1.0, self.braking_skill))
