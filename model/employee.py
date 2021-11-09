from dataclasses import dataclass
from functools import total_ordering
from flask.json import JSONEncoder

@dataclass
@total_ordering
class Employee:
    def __init__(self, id):
        self.id = id
        self.low, self.medium, self.high, self.critical = [],[],[],[]

    def add_incident(self, incident_obj):
        priority = incident_obj.priority
        if priority == 'low':
            self.low.append(incident_obj)
        elif priority == 'medium':
            self.medium.append(incident_obj)
        elif priority == 'high':
            self.high.append(incident_obj)
        elif priority == 'critical':
            self.critical.append(incident_obj)

    def get_incidents(self, priority):
        if priority == 'low':
            self.low.sort()
            return self.low
        elif priority == 'medium':
            self.medium.sort()
            return self.medium
        elif priority == 'high':
            self.high.sort()
            return self.high
        elif priority == 'critical':
            self.critical.sort()
            return self.critical

    def sort_incidents(self):
        all_incidents = [self.low, self.medium, self.high, self.critical]
        for incident in all_incidents:
            incident.sort()

    def to_json(self):
        return {"low": {"count": len(self.low), "incidents": [_.to_json() for _ in self.low]},
                "medium": {"count": len(self.medium), "incidents": [_.to_json() for _ in self.medium]},
                "high": {"count": len(self.high), "incidents": [_.to_json() for _ in self.high]},
                "critical": {"count": len(self.critical), "incidents": [_.to_json() for _ in self.critical]}}

    def __lt__(self, other: object):
        if not isinstance(other, Employee):
            return NotImplemented
        else:
            return self.id < other.id

    def __eq__(self, other: object):
        if not isinstance(other, Employee):
            return NotImplemented
        else:
            return self.id == other.id

class EmployeeEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, Employee):
            return o.to_json()
        return JSONEncoder.default(self, o)
