from dataclasses import dataclass
from enum import Enum, unique
from typing import Dict


@unique
class StringConstants(Enum):
    event_type = 'event_type'


@dataclass
class EventType:
    name: str
    conditions: Dict


def load_event_types_from_json(config_events: Dict) -> Dict:
    event_types = []
    for config_event in config_events:
            event_types.append(EventType(config_event['name'], config_event['conditions']))
    return event_types
