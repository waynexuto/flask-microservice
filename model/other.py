from dataclasses import dataclass
from functools import total_ordering
from flask.json import JSONEncoder
from model.basemodel import BaseModel

@dataclass
@total_ordering
class Other(BaseModel):
    def __init__(self, priority, identifier, timestamp):
        self.type = "other"
        self.priority = priority
        self.identifier = identifier
        self.timestamp = timestamp

    def to_json(self):
        return {"type": "other", "priority": self.priority, "identifier": self.identifier,
                "timestamp": self.timestamp}

    def __lt__(self, other: object):
        if not isinstance(other, Other):
            return NotImplemented
        else:
            return self.timestamp < other.timestamp

    def __eq__(self, other: object):
        if not isinstance(other, Other):
            return NotImplemented
        else:
            return self.timestamp == other.timestamp

class OtherEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o,Other):
            return o.to_json()
        return JSONEncoder.default(self, o)
