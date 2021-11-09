from dataclasses import dataclass
from functools import total_ordering
from flask.json import JSONEncoder
from model.basemodel import BaseModel

@dataclass
@total_ordering
class Probing(BaseModel):
    def __init__(self, priority, ip, timestamp):
        self.type = "probing"
        self.priority = priority
        self.ip = ip
        self.timestamp = timestamp

    def to_json(self):
        return {"type": "probing", "priority": self.priority, "ip": self.ip, "timestamp": self.timestamp}

    def __lt__(self, other: object):
        if not isinstance(other, Probing):
            return NotImplemented
        else:
            return self.timestamp < other.timestamp

    def __eq__(self, other: object):
        if not isinstance(other, Probing):
            return NotImplemented
        else:
            return self.timestamp == other.timestamp

class ProbingEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o,Probing):
            return o.to_json()
        return JSONEncoder.default(self, o)
