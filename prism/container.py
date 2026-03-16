"""Composition root — the ONLY file that imports concrete classes.

All DI wiring happens here. No other module should import concrete
implementations directly; they receive interfaces via constructors.
"""

from __future__ import annotations

from pathlib import Path

from prism.accessors.command_accessor.command_accessor import CommandAccessor
from prism.accessors.file_accessor.file_accessor import FileAccessor
from prism.accessors.registry_accessor.registry_accessor import RegistryAccessor
from prism.accessors.rollback_accessor.rollback_accessor import RollbackAccessor
from prism.accessors.sudo_accessor.sudo_accessor import SudoAccessor
from prism.accessors.system_accessor.system_accessor import SystemAccessor
from prism.engines.config_engine.config_engine import ConfigEngine
from prism.engines.installation_engine.installation_engine import InstallationEngine
from prism.managers.installation_manager.installation_manager import InstallationManager
from prism.managers.package_manager.package_manager import PackageManager
from prism.utilities.event_bus.local_event_bus import LocalEventBus


class Container:
    """DI container — builds the full object graph.

    Usage:
        container = Container(prisms_dir=Path("prisms"))
        result = container.installation_manager.install("startup.prism", user_info)
        packages = container.package_manager.list_packages()
    """

    def __init__(self, prisms_dir: Path | None = None) -> None:
        if prisms_dir is None:
            prisms_dir = Path(__file__).parent / "prisms"
        self._prisms_dir = prisms_dir

        # Utilities
        self.event_bus = LocalEventBus()

        # Engines
        self.config_engine = ConfigEngine()
        self.installation_engine = InstallationEngine(
            command_accessor=CommandAccessor(),
            file_accessor=FileAccessor(),
            system_accessor=SystemAccessor(),
            rollback_accessor=RollbackAccessor(),
        )

        # Accessors (for manager-level use)
        self.file_accessor = FileAccessor()
        self.system_accessor = SystemAccessor()
        self.registry_accessor = RegistryAccessor()
        self.sudo_accessor = SudoAccessor()

        # Managers
        self.installation_manager = InstallationManager(
            config_engine=self.config_engine,
            installation_engine=self.installation_engine,
            file_accessor=self.file_accessor,
            system_accessor=self.system_accessor,
            event_bus=self.event_bus,
            prisms_dir=self._prisms_dir,
        )

        self.package_manager = PackageManager(
            config_engine=self.config_engine,
            file_accessor=self.file_accessor,
            prisms_dir=self._prisms_dir,
        )
