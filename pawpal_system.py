"""Data models and scheduling interface for the PawPal+ pet care planner."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum
from uuid import UUID, uuid4


class Recurrence(str, Enum):
    """How often a care task repeats."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class CareTask:
    """A care activity associated with a specific pet."""

    name: str
    category: str
    duration_minutes: int
    priority_level: str
    recurrence: Recurrence = Recurrence.DAILY
    time_window_start: time | None = None
    time_window_end: time | None = None
    id: UUID = field(default_factory=uuid4)


@dataclass
class Pet:
    """A pet and the care tasks associated with it."""

    name: str
    species: str
    age: int
    care_tasks: list[CareTask] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)


@dataclass
class DailyPlan:
    """The selected, ordered care tasks for one pet on one date."""

    pet_id: UUID
    date: date
    scheduled_tasks: list[CareTask] = field(default_factory=list)
    reasoning: str = ""
    id: UUID = field(default_factory=uuid4)

    @property
    def total_duration_minutes(self) -> int:
        """Calculate total planned time from the tasks in this plan."""
        return sum(task.duration_minutes for task in self.scheduled_tasks)


@dataclass
class Owner:
    """An owner, their preferences, pets, and generated plans."""

    name: str
    preferences: str
    time_availability_minutes: int
    pets: list[Pet] = field(default_factory=list)
    daily_plans: list[DailyPlan] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def add_task(self, pet_id: UUID, task: CareTask) -> None:
        """Add a care task to the specified pet."""
        raise NotImplementedError

    def edit_task(
        self,
        pet_id: UUID,
        task_id: UUID,
        updated_task: CareTask,
    ) -> None:
        """Replace a task identified by its pet and task IDs."""
        raise NotImplementedError

    def remove_task(self, pet_id: UUID, task_id: UUID) -> None:
        """Remove a task identified by its pet and task IDs."""
        raise NotImplementedError

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's collection."""
        raise NotImplementedError

    def edit_pet(self, pet_id: UUID, updated_pet: Pet) -> None:
        """Replace a pet identified by its ID."""
        raise NotImplementedError


@dataclass
class Scheduler:
    """Select and order a pet's care tasks within the owner's constraints."""

    def generate_plan(
        self,
        owner: Owner,
        pet: Pet,
        plan_date: date,
    ) -> DailyPlan:
        """Create a daily plan from the pet's tasks and owner constraints."""
        raise NotImplementedError

    def sort_tasks_by_priority(self, tasks: list[CareTask]) -> list[CareTask]:
        """Return tasks ordered by priority."""
        raise NotImplementedError

    def select_tasks_within_time(
        self,
        tasks: list[CareTask],
        available_minutes: int,
    ) -> list[CareTask]:
        """Select tasks that fit within the available time."""
        raise NotImplementedError

    def explain_reasoning(
        self,
        selected_tasks: list[CareTask],
        skipped_tasks: list[CareTask],
    ) -> str:
        """Explain why tasks were selected, ordered, or skipped."""
        raise NotImplementedError
