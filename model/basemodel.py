from dataclasses import dataclass


@dataclass
class BaseModel:
    @classmethod
    def from_json(cls, json_dict):
        return cls(**json_dict)
