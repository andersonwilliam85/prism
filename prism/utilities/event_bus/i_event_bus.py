"""IEventBus — foundational utility for manager-to-manager async communication.

Managers NEVER call each other directly. They publish events that other
managers subscribe to. This is the standard IDesign pattern for
manager-to-manager communication.
"""

from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable


@runtime_checkable
class IEventBus(Protocol):
    """Publish/subscribe event bus for async manager-to-manager communication."""

    def publish(self, event_type: str, payload: dict) -> None: ...

    def subscribe(self, event_type: str, handler: Callable[[dict], None]) -> None: ...
