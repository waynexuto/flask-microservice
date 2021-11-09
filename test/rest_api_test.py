import unittest
import fakeredis
from app import service
from model.denial import Denial
from model.employee import Employee


class TestService(unittest.TestCase):

    def setUp(self):
        self.server = fakeredis.FakeServer()
        self.server.connected = True
        self.cache = fakeredis.FakeRedis(server=self.server)

    def test_create_incident_from_json(self):
        denial = {"priority": "high", "reported_by": 2, "timestamp": 2, "source_ip": "215.249.6.62"}
        self.employee_id, self.actual = service.create_incident_from_json('denial',denial, self.cache)
        assert self.actual.priority == "high"
        assert self.actual.reported_by == 2
        assert self.actual.timestamp == 2
        assert self.actual.source_ip == "215.249.6.62"
        assert self.employee_id == 2

    def test_append_employee_group(self):
        denial = {"priority": "high", "reported_by": 2, "timestamp": 2, "source_ip": "215.249.6.62"}
        self.employee_id, self.actual = service.create_incident_from_json('denial', denial, self.cache)
        self.actual_employee = service.append_employee_group(2, self.actual, [])
        denial = Denial("high", 2, 2, "215.249.6.62")
        self.expected_employee = Employee(2)
        self.expected_employee.add_incident(denial)
        assert self.expected_employee == self.actual_employee
        assert self.expected_employee.get_incidents("high") == self.actual_employee.get_incidents("high")

    def tearDown(self):
        self.cache = None
        self.server = None

if __name__ == "__main__":
    unittest.main()