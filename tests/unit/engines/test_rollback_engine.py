"""Unit tests for RollbackEngine — pure logic, no I/O."""

from __future__ import annotations

from prism.engines.rollback_engine.rollback_engine import RollbackEngine


class TestCreateState:
    def test_creates_empty_state(self) -> None:
        engine = RollbackEngine()
        state = engine.create_state("test-prism")
        assert state.package_name == "test-prism"
        assert state.actions == []
        assert state.rolled_back is False


class TestRecordAction:
    def test_records_action(self) -> None:
        engine = RollbackEngine()
        state = engine.create_state("test-prism")
        engine.record_action(state, "file_created", "/tmp/test.txt")
        assert len(state.actions) == 1
        assert state.actions[0].action_type == "file_created"
        assert state.actions[0].target == "/tmp/test.txt"

    def test_records_with_rollback_command(self) -> None:
        engine = RollbackEngine()
        state = engine.create_state("test-prism")
        engine.record_action(state, "command_executed", "npm install", rollback_command="npm uninstall")
        assert state.actions[0].rollback_command == "npm uninstall"

    def test_records_with_original_value(self) -> None:
        engine = RollbackEngine()
        state = engine.create_state("test-prism")
        engine.record_action(state, "config_changed", "git.user.name", original_value="old-name")
        assert state.actions[0].original_value == "old-name"


class TestComputeRollbackPlan:
    def test_lifo_order(self) -> None:
        engine = RollbackEngine()
        state = engine.create_state("test-prism")
        engine.record_action(state, "file_created", "/tmp/a.txt")
        engine.record_action(state, "file_created", "/tmp/b.txt")
        engine.record_action(state, "file_created", "/tmp/c.txt")
        plan = engine.compute_rollback_plan(state)
        assert [a.target for a in plan] == ["/tmp/c.txt", "/tmp/b.txt", "/tmp/a.txt"]

    def test_includes_auto_rollback_types(self) -> None:
        engine = RollbackEngine()
        state = engine.create_state("test-prism")
        engine.record_action(state, "file_created", "/tmp/file.txt")
        engine.record_action(state, "dir_created", "/tmp/dir")
        plan = engine.compute_rollback_plan(state)
        assert len(plan) == 2

    def test_includes_explicit_rollback_commands(self) -> None:
        engine = RollbackEngine()
        state = engine.create_state("test-prism")
        engine.record_action(state, "command_executed", "npm install", rollback_command="npm uninstall")
        plan = engine.compute_rollback_plan(state)
        assert len(plan) == 1
        assert plan[0].rollback_command == "npm uninstall"

    def test_includes_config_with_original(self) -> None:
        engine = RollbackEngine()
        state = engine.create_state("test-prism")
        engine.record_action(state, "config_changed", "key", original_value="old")
        plan = engine.compute_rollback_plan(state)
        assert len(plan) == 1

    def test_skips_actions_without_rollback(self) -> None:
        engine = RollbackEngine()
        state = engine.create_state("test-prism")
        engine.record_action(state, "command_executed", "some-side-effect")  # no rollback_command
        engine.record_action(state, "config_changed", "key")  # no original_value
        plan = engine.compute_rollback_plan(state)
        assert len(plan) == 0


class TestValidateCompleteness:
    def test_all_covered(self) -> None:
        engine = RollbackEngine()
        state = engine.create_state("test-prism")
        engine.record_action(state, "file_created", "/tmp/file.txt")
        engine.record_action(state, "dir_created", "/tmp/dir")
        ok, warnings = engine.validate_completeness(state)
        assert ok is True
        assert warnings == []

    def test_missing_rollback(self) -> None:
        engine = RollbackEngine()
        state = engine.create_state("test-prism")
        engine.record_action(state, "package_installed", "docker")
        ok, warnings = engine.validate_completeness(state)
        assert ok is False
        assert len(warnings) == 1
        assert "docker" in warnings[0]

    def test_mixed_coverage(self) -> None:
        engine = RollbackEngine()
        state = engine.create_state("test-prism")
        engine.record_action(state, "file_created", "/tmp/ok.txt")
        engine.record_action(state, "package_installed", "node", rollback_command="brew uninstall node")
        engine.record_action(state, "command_executed", "no-undo")
        ok, warnings = engine.validate_completeness(state)
        assert ok is False
        assert len(warnings) == 1
        assert "no-undo" in warnings[0]
