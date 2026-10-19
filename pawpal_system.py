"""Core data models and scheduling behavior for the PawPal+ pet care planner."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum
from uuid import UUID, uuid4


class Frequency(str, Enum):
    """Supported recurrence patterns for tasks."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    """A single pet-care activity, its schedule, and completion state."""

    description: str
    duration_minutes: int
    priority_level: str
    frequency: Frequency = Frequency.DAILY
    scheduled_time: time | None = None
    scheduled_date: date | None = None
    days_of_week: set[int] = field(default_factory=set)
    completed: bool = False
    completed_dates: set[date] = field(default_factory=set)
    id: UUID = field(default_factory=uuid4)
    pet_id: UUID | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Validate the task's description, duration, priority, and recurrence."""
        if not self.description.strip():
            raise ValueError("Task description cannot be empty.")
        if self.duration_minutes <= 0:
            raise ValueError("Task duration must be greater than zero minutes.")
        if self.priority_level not in {"low", "medium", "high"}:
            raise ValueError("Priority must be 'low', 'medium', or 'high'.")
        if not isinstance(self.frequency, Frequency):
            self.frequency = Frequency(self.frequency)
        if self.frequency is Frequency.ONCE and self.scheduled_date is None:
            raise ValueError("One-time tasks must have a scheduled_date.")
        if self.frequency is Frequency.WEEKLY and not self.days_of_week:
            raise ValueError("Weekly tasks must specify at least one weekday.")
        if any(day < 0 or day > 6 for day in self.days_of_week):
            raise ValueError("Weekdays must use date.weekday() values from 0 to 6.")

    def is_due_on(self, day: date) -> bool:
        """Whether this task is due on the given date and is still incomplete."""
        if not self.occurs_on(day):
            return False
        if self.frequency is Frequency.ONCE:
            return not self.completed
        return day not in self.completed_dates

    def occurs_on(self, day: date) -> bool:
        """Whether this task's recurrence falls on the given date."""
        if self.frequency is Frequency.ONCE:
            return self.scheduled_date == day
        if self.frequency is Frequency.WEEKLY:
            return day.weekday() in self.days_of_week
        return True

    def mark_complete(self, completed_on: date | None = None) -> None:
        """Mark this one-time task or recurring occurrence as completed."""
        completed_on = completed_on or date.today()
        if not self.occurs_on(completed_on):
            raise ValueError(f"Task is not scheduled for {completed_on}.")
        if self.frequency is Frequency.ONCE:
            self.completed = True
        else:
            self.completed_dates.add(completed_on)


@dataclass
class Pet:
    """A pet and the tasks that belong specifically to that pet."""

    name: str
    species: str
    age: int
    care_tasks: list[Task] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def add_task(self, task: Task) -> None:
        """Associate a task with this pet and add it to the pet's task list."""
        if any(existing.id == task.id for existing in self.care_tasks):
            raise ValueError(f"Task {task.id} already belongs to pet {self.id}.")
        if task.pet_id is not None and task.pet_id != self.id:
            raise ValueError(f"Task {task.id} already belongs to another pet.")
        task.pet_id = self.id
        self.care_tasks.append(task)

    def edit_task(self, task_id: UUID, updated_task: Task) -> None:
        """Replace a task while retaining its identity and pet association."""
        index = self._task_index(task_id)
        if updated_task.id != task_id:
            raise ValueError("An edited task must retain the original task ID.")
        if updated_task.pet_id not in {None, self.id}:
            raise ValueError("The updated task belongs to another pet.")
        updated_task.pet_id = self.id
        self.care_tasks[index] = updated_task

    def remove_task(self, task_id: UUID) -> Task:
        """Remove and return a task by its ID."""
        return self.care_tasks.pop(self._task_index(task_id))

    def _task_index(self, task_id: UUID) -> int:
        for index, task in enumerate(self.care_tasks):
            if task.id == task_id:
                return index
        raise KeyError(f"No task with ID {task_id} belongs to pet {self.id}.")


@dataclass
class Owner:
    """An owner who manages multiple pets and their care tasks."""

    name: str
    preferences: str = ""
    time_availability_minutes: int = 240
    pets: list[Pet] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        """Ensure the owner's available time is not negative."""
        if self.time_availability_minutes < 0:
            raise ValueError("Available time cannot be negative.")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner, rejecting duplicate pet IDs."""
        if any(existing.id == pet.id for existing in self.pets):
            raise ValueError(f"Pet {pet.id} already belongs to this owner.")
        self.pets.append(pet)

    def get_pet(self, pet_id: UUID) -> Pet:
        """Return an owned pet by ID or raise KeyError if it is not found."""
        for pet in self.pets:
            if pet.id == pet_id:
                return pet
        raise KeyError(f"No pet with ID {pet_id} belongs to owner {self.id}.")

    def remove_pet(self, pet_id: UUID) -> Pet:
        """Remove and return an owned pet by ID."""
        for index, pet in enumerate(self.pets):
            if pet.id == pet_id:
                return self.pets.pop(index)
        raise KeyError(f"No pet with ID {pet_id} belongs to owner {self.id}.")

    def add_task(self, pet_id: UUID, task: Task) -> None:
        """Add a task to the specified pet."""
        self.get_pet(pet_id).add_task(task)

    def edit_task(
        self,
        pet_id: UUID,
        task_id: UUID,
        updated_task: Task,
    ) -> None:
        """Edit a task belonging to the specified pet."""
        self.get_pet(pet_id).edit_task(task_id, updated_task)

    def remove_task(self, pet_id: UUID, task_id: UUID) -> Task:
        """Remove and return a task belonging to the specified pet."""
        return self.get_pet(pet_id).remove_task(task_id)

    def get_all_tasks(self) -> list[Task]:
        """Return a new list containing the tasks of every owned pet."""
        return [task for pet in self.pets for task in pet.care_tasks]


@dataclass
class Scheduler:
    """Retrieve and organize incomplete care tasks across an owner's pets."""

    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def get_tasks(
        self,
        owner: Owner,
        *,
        plan_date: date | None = None,
        include_completed: bool = False,
    ) -> list[Task]:
        """Retrieve tasks from the owner-wide task collection, optionally due-filtered."""
        tasks = owner.get_all_tasks()
        if plan_date is not None:
            is_relevant = (
                (lambda task: task.occurs_on(plan_date))
                if include_completed
                else (lambda task: task.is_due_on(plan_date))
            )
            tasks = [task for task in tasks if is_relevant(task)]
        elif not include_completed:
            tasks = [task for task in tasks if not task.completed]
        return tasks

    def organize_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by scheduled time, putting tasks without a time last."""
        return sorted(
            tasks,
            key=lambda task: (
                task.scheduled_time is None,
                task.scheduled_time or time.max,
            ),
        )

    def generate_schedule(
        self,
        owner: Owner,
        plan_date: date,
        available_minutes: int | None = None,
    ) -> list[Task]:
        """Return prioritized due tasks that fit the owner's available time."""
        budget = (
            owner.time_availability_minutes
            if available_minutes is None
            else available_minutes
        )
        if budget < 0:
            raise ValueError("Available time cannot be negative.")

        due_tasks = self.get_tasks(owner, plan_date=plan_date)
        ordered_tasks = self.organize_tasks(due_tasks)
        scheduled: list[Task] = []
        remaining_minutes = budget

        for task in ordered_tasks:
            if task.duration_minutes <= remaining_minutes:
                scheduled.append(task)
                remaining_minutes -= task.duration_minutes
        return scheduled

    def mark_task_complete(
        self,
        owner: Owner,
        task_id: UUID,
        completed_on: date | None = None,
    ) -> None:
        """Mark one task complete by searching across all of the owner's pets."""
        matches = [task for task in owner.get_all_tasks() if task.id == task_id]
        if not matches:
            raise KeyError(f"No task with ID {task_id} belongs to this owner.")
        if len(matches) > 1:
            raise ValueError(f"Task ID {task_id} is not unique across this owner.")
        matches[0].mark_complete(completed_on or date.today())
