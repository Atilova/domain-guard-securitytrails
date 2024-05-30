from typing import Protocol, Any


class IGatewayProducer(Protocol):
    """IGatewayProducer"""

    def produce_json(self, data: dict[str, Any]):
        pass