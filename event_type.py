from dataclasses import dataclass
from typing import Dict

event_type_str = 'event_type'

@dataclass
class EventType:
    name: str
    conditions: Dict
