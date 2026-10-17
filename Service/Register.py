
import json
from pathlib import Path

from Model.Node import Node
from Model.Edge import Edge
from Service.EmbeddingService import EmbeddingService


class RegisterService:
    def __init__(self, embedding_service=None):
        self.embedding_service = embedding_service or EmbeddingService()

    def register(self, json_path: str | Path) -> None:
        json_path = Path(json_path)

        if not json_path.is_absolute():
            json_path = Path.cwd() / json_path

        if not json_path.is_file():
            raise FileNotFoundError(
                f"Registration file not found: {json_path}"
            )

        with json_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        nodes = data.get("Nodes", [])
        edges = data.get("Edges", [])

        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise ValueError("'Nodes' and 'Edges' must be lists")

        # Validate node definitions.
        node_ids = set()

        for node_data in nodes:
            node_id = node_data["Id"]
            answer = node_data["Answer"]

            if not isinstance(node_id, int) or isinstance(node_id, bool):
                raise ValueError(f"Invalid node ID: {node_id}")

            if node_id in node_ids:
                raise ValueError(f"Duplicate node ID: {node_id}")

            if not isinstance(answer, str):
                raise ValueError(f"Invalid answer for node {node_id}")

            node_ids.add(node_id)

        # Validate edge definitions and references.
        for index, edge_data in enumerate(edges, start=1):
            start_id = edge_data["StartNodeId"]
            destination_id = edge_data["DestinationNodeId"]
            response = edge_data["UserResponse"]

            if start_id not in node_ids:
                raise ValueError(f"Unknown start node: {start_id}")

            if destination_id not in node_ids:
                raise ValueError(
                    f"Unknown destination node: {destination_id}"
                )

            if not isinstance(response, str) or not response.strip():
                raise ValueError(
                    f"UserResponse cannot be empty (edge {index})"
                )

        # Save nodes.
        for node_data in nodes:
            Node(
                Id=node_data["Id"],
                Answer=node_data["Answer"]
            ).save()

        # Determine the next unique edge ID.
        existing_edges = Edge.get_all()

        existing_ids = [
            edge.Id
            for edge in existing_edges
            if getattr(edge, "Id", None) is not None
        ]

        next_edge_id = max(existing_ids, default=0) + 1

        # Encode and save every edge independently.
        for edge_data in edges:
            response = edge_data["UserResponse"]
            embedding = self.embedding_service.encode(response)

            Edge(
                Id=next_edge_id,
                NodeFromID=edge_data["StartNodeId"],
                NodeToID=edge_data["DestinationNodeId"],
                UserResponse=response,
                Embedding=embedding
            ).save()

            next_edge_id += 1

        print(
            f"Registered {len(nodes)} nodes and "
            f"{len(edges)} edges from {json_path.name}"
        )
