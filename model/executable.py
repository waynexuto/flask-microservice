from dataclasses import dataclass
from functools import total_ordering
from flask.json import JSONEncoder
from model.basemodel import BaseModel

@dataclass
@total_ordering
class Executable(BaseModel):
    def __init__(self, priority, machine_ip, timestamp):
        self.type = "executable"
        self.priority = priority
        self.machine_ip = machine_ip
        self.timestamp = timestamp

    def to_json(self):
        return {"type": "executable", "priority": self.priority, "machine_ip": self.machine_ip,
                "timestamp": self.timestamp}

    def __lt__(self, other: object):
        if not isinstance(other, Executable):
            return NotImplemented
        else:
            return self.timestamp < other.timestamp

    def __eq__(self, other: object):
        if not isinstance(other, Executable):
            return NotImplemented
        else:
            return self.timestamp == other.timestamp

class ExecutableEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o,Executable):
            return o.to_json()
        return JSONEncoder.default(self, o)