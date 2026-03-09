"""Composition root — the ONLY file that imports concrete classes.

All DI wiring happens here. No other module should import concrete
implementations directly; they receive interfaces via constructors.
"""

from __future__ import annotations

from pathlib import Path

from prism.accessors.command_accessor.command_accessor import CommandAccessor
from prism.accessors.file_accessor.file_accessor import FileAccessor
from prism.accessors.registry_accessor.registry_accessor import RegistryAccessor
from prism.accessors.system_accessor.system_accessor import SystemAccessor
from prism.engines.merge_engine.merge_engine import MergeEngine
from prism.engines.resolution_engine.resolution_engine import ResolutionEngine
from prism.engines.scaffold_engine.scaffold_engine import ScaffoldEngine
from prism.engines.setup_engine.setup_engine import SetupEngine
from prism.engines.validation_engine.validation_engine import ValidationEngine
from prism.managers.installation_manager.installation_manager import InstallationManager
from prism.managers.package_manager.package_manager import PackageManager
from prism.utilities.event_bus.in_memory_event_bus import InMemoryEventBus


class Container:
    """DI container — builds the full object graph.

    Usage:
        container = Container(prisms_dir=Path("prisms"))
        result = container.installation_manager.install("startup.prism", user_info)
        packages = container.package_manager.list_packages()
    """

    def __init__(self, prisms_dir: Path | None = None) -> None:
        if prisms_dir is None:
            prisms_dir = Path(__file__).parent.parent / "prisms"
        self._prisms_dir = prisms_dir

        # Utilities
        self.event_bus = InMemoryEventBus()

        # Engines
        self.merge_engine = MergeEngine()
        self.resolution_engine = ResolutionEngine()
        self.scaffold_engine = ScaffoldEngine()
        self.setup_engine = SetupEngine()
        self.validation_engine = ValidationEngine()

        # Accessors
        self.command_accessor = CommandAccessor()
        self.file_accessor = FileAccessor()
        self.system_accessor = SystemAccessor()
        self.registry_accessor = RegistryAccessor()

        # Managers
        self.installation_manager = InstallationManager(
            merge_engine=self.merge_engine,
            setup_engine=self.setup_engine,
            validation_engine=self.validation_engine,
            command_accessor=self.command_accessor,
            file_accessor=self.file_accessor,
            system_accessor=self.system_accessor,
            event_bus=self.event_bus,
            prisms_dir=self._prisms_dir,
        )

        self.package_manager = PackageManager(
            validation_engine=self.validation_engine,
            file_accessor=self.file_accessor,
            prisms_dir=self._prisms_dir,
        )
