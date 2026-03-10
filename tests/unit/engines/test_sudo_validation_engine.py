"""Unit tests for SudoValidationEngine — pure logic, no subprocess."""

from __future__ import annotations

from datetime import datetime, timedelta

from prism.engines.sudo_validation_engine.sudo_validation_engine import SudoValidationEngine
from prism.models.installation import SudoSession


class TestCreateSession:
    def test_creates_session_with_unique_token(self) -> None:
        engine = SudoValidationEngine()
        s1 = engine.create_session()
        s2 = engine.create_session()
        assert s1.token != s2.token

    def test_session_starts_with_zero_attempts(self) -> None:
        engine = SudoValidationEngine()
        session = engine.create_session()
        assert session.attempts == 0
        assert session.locked_until is None

    def test_session_not_expired_when_new(self) -> None:
        engine = SudoValidationEngine()
        session = engine.create_session()
        assert not session.is_expired
        assert engine.validate_session(session)


class TestValidateSession:
    def test_valid_session(self) -> None:
        engine = SudoValidationEngine()
        session = engine.create_session()
        assert engine.validate_session(session) is True

    def test_expired_session(self) -> None:
        engine = SudoValidationEngine()
        session = SudoSession(
            token="test",
            created_at=datetime.now() - timedelta(hours=1),
            ttl_seconds=60,
        )
        assert session.is_expired
        assert engine.validate_session(session) is False

    def test_locked_session(self) -> None:
        engine = SudoValidationEngine()
        session = SudoSession(
            token="test",
            locked_until=datetime.now() + timedelta(seconds=30),
        )
        assert session.is_locked
        assert engine.validate_session(session) is False

    def test_past_lockout_is_valid(self) -> None:
        engine = SudoValidationEngine()
        session = SudoSession(
            token="test",
            locked_until=datetime.now() - timedelta(seconds=1),
        )
        assert not session.is_locked
        assert engine.validate_session(session) is True


class TestRecordAttempt:
    def test_success_resets_attempts(self) -> None:
        engine = SudoValidationEngine()
        session = SudoSession(token="test", attempts=2)
        updated = engine.record_attempt(session, success=True)
        assert updated.attempts == 0
        assert updated.locked_until is None

    def test_failure_increments_attempts(self) -> None:
        engine = SudoValidationEngine()
        session = SudoSession(token="test", attempts=0)
        updated = engine.record_attempt(session, success=False)
        assert updated.attempts == 1
        assert updated.locked_until is None

    def test_locks_after_max_attempts(self) -> None:
        engine = SudoValidationEngine()
        session = SudoSession(token="test", attempts=2, max_attempts=3)
        updated = engine.record_attempt(session, success=False)
        assert updated.attempts == 3
        assert updated.locked_until is not None
        assert updated.is_locked

    def test_success_after_lockout_resets(self) -> None:
        engine = SudoValidationEngine()
        session = SudoSession(
            token="test",
            attempts=3,
            locked_until=datetime.now() - timedelta(seconds=1),
        )
        updated = engine.record_attempt(session, success=True)
        assert updated.attempts == 0
        assert updated.locked_until is None
