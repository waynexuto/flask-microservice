from dataclasses import dataclass
from functools import total_ordering
from flask.json import JSONEncoder
from model.basemodel import BaseModel


@dataclass
@total_ordering
class Denial(BaseModel):
    def __init__(self, priority, reported_by, timestamp, source_ip):
        self.type = "denial"
        self.priority = priority
        self.reported_by = reported_by
        self.timestamp = timestamp
        self.source_ip = source_ip

    def to_json(self):
        return {"type": "denial", "priority": self.priority, "reported_by": self.reported_by,
                "timestamp": self.timestamp, "source_ip": self.source_ip}

    def __lt__(self, other: object):
        if not isinstance(other, Denial):
            return NotImplemented
        else:
            return self.timestamp < other.timestamp

    def __eq__(self, other: object):
        if not isinstance(other, Denial):
            return NotImplemented
        else:
            return self.timestamp == other.timestamp

class DenialEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o,Denial):
            return o.to_json()
        return JSONEncoder.default(self, o)
