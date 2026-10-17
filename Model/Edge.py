
import json
from pathlib import Path


class Edge:
    DB_PATH = (
        Path(__file__).resolve().parent.parent / "DB" / "Edge.json"
    )

    def __init__(
        self,
        Id: int,
        NodeFromID: int,
        NodeToID: int,
        UserResponse: str,
        Embedding: list[float]
    ):
        if not isinstance(Id, int) or isinstance(Id, bool) or Id < 1:
            raise ValueError("Edge Id must be a positive integer")

        self.Id = Id
        self.NodeFromID = NodeFromID
        self.NodeToID = NodeToID
        self.UserResponse = UserResponse
        self.Embedding = Embedding

    def to_dict(self) -> dict:
        return {
            "Id": self.Id,
            "NodeFromID": self.NodeFromID,
            "NodeToID": self.NodeToID,
            "UserResponse": self.UserResponse,
            "Embedding": self.Embedding
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            Id=data["Id"],
            NodeFromID=data["NodeFromID"],
            NodeToID=data["NodeToID"],
            UserResponse=data["UserResponse"],
            Embedding=data["Embedding"]
        )

    @classmethod
    def _read_all(cls) -> list:
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        if not cls.DB_PATH.exists():
            cls.DB_PATH.write_text("[]", encoding="utf-8")
            return []

        content = cls.DB_PATH.read_text(encoding="utf-8").strip()

        if not content:
            cls.DB_PATH.write_text("[]", encoding="utf-8")
            return []

        data = json.loads(content)

        if not isinstance(data, list):
            raise ValueError("Edge database must contain a JSON list")

        return data

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
        allowed_fields = {
            "Id",
            "NodeFromID",
            "NodeToID",
            "UserResponse",
            "Embedding"
        }

        unknown_fields = set(kwargs) - allowed_fields

        if unknown_fields:
            raise ValueError(
                f"Unknown filter fields: {sorted(unknown_fields)}"
            )

        return [
            cls.from_dict(item)
            for item in cls._read_all()
            if all(item.get(key) == value for key, value in kwargs.items())
        ]

    @classmethod
    def get_outgoing(cls, NodeFromID: int) -> list:
        return cls.filter(NodeFromID=NodeFromID)

    def delete(self) -> bool:
        data = self._read_all()
        updated = [
            item for item in data
            if item["Id"] != self.Id
        ]

        if len(updated) == len(data):
            return False

        self._write_all(updated)
        return True

    @classmethod
    def delete_by_id(cls, Id: int) -> bool:
        edge = cls.get(Id)
        return edge.delete() if edge is not None else False

    @classmethod
    def next_id(cls) -> int:
        """Generate the next available edge ID."""
        ids = [
            item["Id"]
            for item in cls._read_all()
            if isinstance(item.get("Id"), int)
            and not isinstance(item.get("Id"), bool)
        ]
        return max(ids, default=0) + 1
