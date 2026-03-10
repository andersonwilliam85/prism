"""LocalEventBus — local publish/subscribe event bus.

Suitable for single-process applications. Replace with a persistent
message broker (Redis, RabbitMQ, etc.) when scaling to multiple processes.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Callable


class LocalEventBus:
    """Local publish/subscribe event bus for manager-to-manager communication."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[[dict], None]]] = defaultdict(list)

    def publish(self, event_type: str, payload: dict) -> None:
        for handler in self._handlers[event_type]:
            handler(payload)

    def subscribe(self, event_type: str, handler: Callable[[dict], None]) -> None:
        self._handlers[event_type].append(handler)
