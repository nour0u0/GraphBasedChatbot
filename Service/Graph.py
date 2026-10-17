
from Model.Node import Node
from Model.Edge import Edge
from Service.EmbeddingService import EmbeddingService


class Graph:
    def __init__(
        self,
        Id: int,
        InNodeId: int,
        FallBackNodeId: int,
        FallBackAnswer: str,
        Threshold: float = 0.75,
        embedding_service: EmbeddingService | None = None
    ):
        if not -1.0 <= Threshold <= 1.0:
            raise ValueError("Threshold must be between -1 and 1")

        self.Id = Id
        self.InNodeId = InNodeId
        self.Nodes: list[Node] = []
        self.Edges: list[Edge] = []
        self.FallBackNodeId = FallBackNodeId
        self.ActiveNodeID = InNodeId
        self.FallBackAnswer = FallBackAnswer
        self.Threshold = Threshold
        self.embedding_service = embedding_service or EmbeddingService()

        self.load()

    def load(self):
        """Reload nodes and edges from the database."""
        self.Nodes = Node.get_all()
        self.Edges = Edge.get_all()

        node_ids = {node.Id for node in self.Nodes}

        if self.InNodeId not in node_ids:
            raise ValueError(
                f"Initial node {self.InNodeId} does not exist"
            )

        if self.FallBackNodeId not in node_ids:
            raise ValueError(
                f"Fallback node {self.FallBackNodeId} does not exist"
            )

        edge_ids = set()

        for edge in self.Edges:
            # Validate unique edge IDs when available.
            edge_id = getattr(edge, "Id", None)

            if edge_id is not None:
                if edge_id in edge_ids:
                    raise ValueError(f"Duplicate edge ID: {edge_id}")
                edge_ids.add(edge_id)

            if edge.NodeFromID not in node_ids:
                raise ValueError(
                    f"Edge references missing source node "
                    f"{edge.NodeFromID}"
                )

            if edge.NodeToID not in node_ids:
                raise ValueError(
                    f"Edge references missing destination node "
                    f"{edge.NodeToID}"
                )

            if not isinstance(edge.Embedding, list) or not edge.Embedding:
                raise ValueError(
                    f"Edge {edge_id} has an invalid embedding"
                )

    def get_node(self, NodeId: int) -> Node | None:
        for node in self.Nodes:
            if node.Id == NodeId:
                return node
        return None

    def get_edge(self, EdgeId: int) -> Edge | None:
        """Find an edge by its unique ID."""
        for edge in self.Edges:
            if getattr(edge, "Id", None) == EdgeId:
                return edge
        return None

    def get_outgoing_edges(self, NodeId: int) -> list[Edge]:
        """Return every outgoing edge, including parallel transitions."""
        return [
            edge for edge in self.Edges
            if edge.NodeFromID == NodeId
        ]

    @staticmethod
    def cosine_similarity(
        embedding_a: list[float],
        embedding_b: list[float]
    ) -> float:
        if len(embedding_a) != len(embedding_b):
            raise ValueError("Embedding dimensions do not match")

        # Embeddings are normalized by EmbeddingService.
        return sum(a * b for a, b in zip(embedding_a, embedding_b))

    def process(self, user_prompt: str) -> str:
        if not isinstance(user_prompt, str) or not user_prompt.strip():
            raise ValueError("User prompt cannot be empty")

        user_embedding = self.embedding_service.encode(user_prompt)

        outgoing_edges = self.get_outgoing_edges(self.ActiveNodeID)

        # Terminal node: return the fallback response and reset state.
        if not outgoing_edges:
            self.ActiveNodeID = self.FallBackNodeId
            return self.FallBackAnswer

        # Find the most similar outgoing edge.
        best_edge = None
        best_similarity = float("-inf")

        for edge in outgoing_edges:
            similarity = self.cosine_similarity(
                user_embedding,
                edge.Embedding
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_edge = edge

        # No edge passes the threshold.
        if best_edge is None or best_similarity < self.Threshold:
            self.ActiveNodeID = self.FallBackNodeId
            return self.FallBackAnswer

        # Follow the best matching transition.
        self.ActiveNodeID = best_edge.NodeToID
        destination = self.get_node(self.ActiveNodeID)

        if destination is None:
            raise ValueError(
                f"Destination node {self.ActiveNodeID} does not exist"
            )

        return destination.Answer

    def reset(self):
        """Return the conversation to its initial node."""
        self.ActiveNodeID = self.InNodeId
