
import json
from pathlib import Path


class Node:
    DB_PATH = Path(__file__).resolve().parent.parent / "DB" / "Node.json"

    def __init__(self, Id: int, Answer: str):
        self.Id = Id
        self.Answer = Answer

    def to_dict(self) -> dict:
        return {
            "Id": self.Id,
            "Answer": self.Answer
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Id=data["Id"],
            Answer=data["Answer"]
        )

    @classmethod
    def _read_all(cls) -> list:
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        if not cls.DB_PATH.exists():
            cls.DB_PATH.write_text("[]", encoding="utf-8")

        return json.loads(cls.DB_PATH.read_text(encoding="utf-8"))

    @classmethod
    def _write_all(cls, data: list) -> None:
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.DB_PATH.write_text(
            json.dumps(data, indent=4, ensure_ascii=False),
            encoding="utf-8"
        )

    def save(self):
        data = self._read_all()

        for index, item in enumerate(data):
            if item["Id"] == self.Id:
                data[index] = self.to_dict()
                self._write_all(data)
                return self

        data.append(self.to_dict())
        self._write_all(data)
        return self

    @classmethod
    def get(cls, Id: int):
        for item in cls._read_all():
            if item["Id"] == Id:
                return cls.from_dict(item)
        return None

    @classmethod
    def get_all(cls) -> list:
        return [cls.from_dict(item) for item in cls._read_all()]

    @classmethod
    def filter(cls, **kwargs) -> list:
        return [
            cls.from_dict(item)
            for item in cls._read_all()
            if all(item.get(key) == value for key, value in kwargs.items())
        ]

    def delete(self) -> bool:
        data = self._read_all()
        updated = [item for item in data if item["Id"] != self.Id]

        if len(updated) == len(data):
            return False

        self._write_all(updated)
        return True
