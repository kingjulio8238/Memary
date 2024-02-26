from dataclasses import dataclass
from datetime import datetime

@dataclass
class MemoryItem:
    entity: str
    date: datetime

    def to_dict(self):
        return {
            'entity': self.entity,
            'date': self.date.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            entity=data['entity'],
            date=datetime.fromisoformat(data['date'])
        )
