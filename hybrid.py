"""Core domain models for the autonomous cleaning simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


Position = tuple[int, int]


class CellType(str, Enum):
    FLOOR = "floor"
    OBSTACLE = "obstacle"
    CHARGER = "charger"


@dataclass(slots=True)
class Room:
    name: str
    cells: set[Position]
    priority: int = 1
    room_type: str = "general"
    available_slots: set[int] = field(default_factory=lambda: set(range(8, 18)))
    cleaning_duration: int = 1

    def contains(self, position: Position) -> bool:
        return position in self.cells


@dataclass(slots=True)
class CleaningTask:
    room_name: str
    duration: int
    priority: int
    battery_cost: float
    available_slots: set[int]
    maintenance_required: bool = False
    assigned_slot: int | None = None
    status: str = "Pending"


@dataclass(slots=True, frozen=True)
class State:
    position: Position
    battery: float
    dirty_locations: frozenset[Position]


@dataclass
class KnowledgeBase:
    visited_locations: set[Position] = field(default_factory=set)
    dirty_locations: set[Position] = field(default_factory=set)
    obstacles: set[Position] = field(default_factory=set)
    battery_level: float = 100.0
    beliefs: dict[str, float] = field(default_factory=dict)
    reasoning_log: list[str] = field(default_factory=list)

    def record(self, message: str) -> None:
        self.reasoning_log.append(message)


@dataclass
class Robot:
    position: Position
    battery: float = 100.0
    max_battery: float = 100.0
    move_cost: float = 1.0
    clean_cost: float = 5.0
    cleaned_cells: int = 0
    knowledge: KnowledgeBase = field(default_factory=KnowledgeBase)

    def move_to(self, position: Position) -> None:
        if self.battery < self.move_cost:
            raise RuntimeError("Insufficient battery to move.")
        previous = self.position
        self.position = position
        self.battery = max(0.0, self.battery - self.move_cost)
        self.knowledge.visited_locations.add(position)
        self._sync_battery()
        self.knowledge.record(
            f"Moved from {previous} to {position}; battery decreased "
            f"by {self.move_cost:.1f}% to {self.battery:.1f}%."
        )

    def clean(self, position: Position) -> None:
        if self.battery < self.clean_cost:
            raise RuntimeError("Insufficient battery to clean.")
        self.battery = max(0.0, self.battery - self.clean_cost)
        self.cleaned_cells += 1
        self.knowledge.dirty_locations.discard(position)
        self._sync_battery()
        self.knowledge.record(
            f"Cleaned {position}; battery decreased by {self.clean_cost:.1f}%."
        )

    def recharge(self) -> None:
        gained = self.max_battery - self.battery
        self.battery = self.max_battery
        self._sync_battery()
        self.knowledge.record(f"Recharged at station; restored {gained:.1f}% battery.")

    def snapshot(self, dirty_locations: set[Position]) -> State:
        return State(self.position, self.battery, frozenset(dirty_locations))

    def _sync_battery(self) -> None:
        self.knowledge.battery_level = self.battery

    def as_dict(self) -> dict[str, Any]:
        return {
            "position": self.position,
            "battery": self.battery,
            "cleaned_cells": self.cleaned_cells,
        }
