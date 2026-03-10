"""Tests for prism.utilities.event_bus."""

from prism.utilities.event_bus.i_event_bus import IEventBus
from prism.utilities.event_bus.local_event_bus import LocalEventBus


class TestLocalEventBus:
    def test_implements_protocol(self):
        bus = LocalEventBus()
        assert isinstance(bus, IEventBus)

    def test_publish_triggers_subscriber(self):
        bus = LocalEventBus()
        received = []
        bus.subscribe("test.event", lambda p: received.append(p))
        bus.publish("test.event", {"key": "value"})
        assert received == [{"key": "value"}]

    def test_multiple_subscribers(self):
        bus = LocalEventBus()
        results = []
        bus.subscribe("e", lambda p: results.append("a"))
        bus.subscribe("e", lambda p: results.append("b"))
        bus.publish("e", {})
        assert results == ["a", "b"]

    def test_no_cross_event_leaking(self):
        bus = LocalEventBus()
        received = []
        bus.subscribe("event.a", lambda p: received.append("a"))
        bus.publish("event.b", {})
        assert received == []

    def test_publish_with_no_subscribers(self):
        bus = LocalEventBus()
        bus.publish("orphan.event", {"data": 1})  # should not raise

    def test_payload_passed_to_handler(self):
        bus = LocalEventBus()
        captured = {}
        bus.subscribe("x", lambda p: captured.update(p))
        bus.publish("x", {"package": "test-prism", "status": "complete"})
        assert captured == {"package": "test-prism", "status": "complete"}
