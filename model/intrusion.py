from dataclasses import dataclass
from functools import total_ordering
from flask.json import JSONEncoder
from model.basemodel import BaseModel

@dataclass
@total_ordering
class Intrusion(BaseModel):
    def __init__(self, priority, internal_ip, source_ip, timestamp):
        self.type = "intrusion"
        self.priority = priority
        self.internal_ip = internal_ip
        self.source_ip = source_ip
        self.timestamp = timestamp

    def to_json(self):
        return {"type": "intrusion", "priority": self.priority, "internal_ip": self.internal_ip,
                "source_ip": self.source_ip, "timestamp": self.timestamp}

    def __lt__(self, other: object):
        if not isinstance(other, Intrusion):
            return NotImplemented
        else:
            return self.timestamp < other.timestamp

    def __eq__(self, other: object):
        if not isinstance(other, Intrusion):
            return NotImplemented
        else:
            return self.timestamp == other.timestamp

class IntrusionEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o,Intrusion):
            return o.to_json()
        return JSONEncoder.default(self, o)

