from dataclasses import dataclass
from functools import total_ordering
from flask.json import JSONEncoder
from model.basemodel import BaseModel

@dataclass
@total_ordering
class Misuse(BaseModel):
    def __init__(self, priority, employee_id, timestamp):
        self.type = "misuse"
        self.priority = priority
        self.employee_id = employee_id
        self.timestamp = timestamp

    def to_json(self):
        return {"type": "misuse", "priority": self.priority,
                "employee_id": self.employee_id, "timestamp": self.timestamp}

    def __lt__(self, other: object):
        if not isinstance(other, Misuse):
            return NotImplemented
        else:
            return self.timestamp < other.timestamp

    def __eq__(self, other: object):
        if not isinstance(other, Misuse):
            return NotImplemented
        else:
            return self.timestamp == other.timestamp

class MisuseEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o,Misuse):
            return o.to_json()
        return JSONEncoder.default(self, o)
