"""Data models and method stubs for the PawPal+ pet care planner."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class CareTask:
    """A care activity that may be included in a pet's daily plan."""

    name: str
    category: str
    duration_minutes: int
    priority_level: str
    scheduled_time_occurrence: str


@dataclass
class Pet:
    """A pet and its preferred care activities."""

    name: str
    species: str
    age: int
    preferred_tasks: list[CareTask] = field(default_factory=list)


@dataclass
class Owner:
    """An owner, their preferences, pets, tasks, and available time."""

    name: str
    preferences: str
    time_availability_minutes: int
    pets: list[Pet] = field(default_factory=list)
    tasks: list[CareTask] = field(default_factory=list)
    daily_plans: list[DailyPlan] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        """Add a care task to the owner's task collection."""
        raise NotImplementedError

    def edit_task(self, task: CareTask) -> None:
        """Update an existing care task."""
        raise NotImplementedError

    def remove_task(self, task: CareTask) -> None:
        """Remove a care task from the owner's task collection."""
        raise NotImplementedError

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet collection."""
        raise NotImplementedError

    def edit_pet(self, pet: Pet) -> None:
        """Update an existing pet."""
        raise NotImplementedError


@dataclass
class DailyPlan:
    """A day's scheduled care tasks and the reasoning behind the plan."""

    scheduled_tasks: list[CareTask]
    date: date
    total_duration_minutes: int
    reasoning: str

    def generate_plan(
        self,
        owner: Owner,
        pet: Pet,
        tasks: list[CareTask],
    ) -> DailyPlan:
        """Build a plan for a pet using the owner's constraints and tasks."""
        raise NotImplementedError

    def sort_tasks_by_priority(self, tasks: list[CareTask]) -> list[CareTask]:
        """Return tasks ordered by priority."""
        raise NotImplementedError

    def sort_tasks_by_time(
        self,
        tasks: list[CareTask],
        available_minutes: int,
    ) -> list[CareTask]:
        """Return tasks that fit within the available time."""
        raise NotImplementedError

    def explain_reasoning(self) -> str:
        """Return an explanation for the selected tasks and their order."""
        raise NotImplementedError