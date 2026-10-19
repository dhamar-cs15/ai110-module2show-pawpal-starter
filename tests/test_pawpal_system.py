from __future__ import annotations

from datetime import date, time

import pytest

from pawpal_system import Frequency, Owner, Pet, Scheduler, Task


def make_task(
    description: str,
    duration: int,
    priority: str = "medium",
    *,
    frequency: Frequency = Frequency.DAILY,
    scheduled_time: time | None = None,
    scheduled_date: date | None = None,
    days_of_week: set[int] | None = None,
) -> Task:
    return Task(
        description=description,
        duration_minutes=duration,
        priority_level=priority,
        frequency=frequency,
        scheduled_time=scheduled_time,
        scheduled_date=scheduled_date,
        days_of_week=set() if days_of_week is None else days_of_week,
    )


def test_schedule_reads_tasks_across_all_pets() -> None:
    dog = Pet("Mochi", "dog", 3)
    cat = Pet("Biscuit", "cat", 5)
    dog_task = make_task("Walk", 20, "high")
    cat_task = make_task("Feed", 10, "medium")
    dog.add_task(dog_task)
    cat.add_task(cat_task)
    owner = Owner("Jordan", pets=[dog, cat], time_availability_minutes=30)

    schedule = Scheduler().generate_schedule(owner, date(2026, 10, 18))

    assert schedule == [dog_task, cat_task]
    assert {task.pet_id for task in schedule} == {dog.id, cat.id}


def test_scheduler_prioritizes_tasks_and_skips_ones_that_do_not_fit() -> None:
    pet = Pet("Mochi", "dog", 3)
    high = make_task("Medication", 20, "high", scheduled_time=time(9, 0))
    medium = make_task("Grooming", 30, "medium")
    low = make_task("Enrichment", 5, "low")
    for task in (medium, low, high):
        pet.add_task(task)
    owner = Owner("Jordan", pets=[pet], time_availability_minutes=25)

    schedule = Scheduler().generate_schedule(owner, date(2026, 10, 18))

    assert schedule == [high, low]


def test_completed_and_not_due_tasks_are_excluded() -> None:
    pet = Pet("Mochi", "dog", 3)
    completed = make_task(
        "Already done",
        5,
        frequency=Frequency.ONCE,
        scheduled_date=date(2026, 10, 17),
    )
    completed.mark_complete(date(2026, 10, 17))
    one_time_future = make_task(
        "Future appointment",
        10,
        frequency=Frequency.ONCE,
        scheduled_date=date(2026, 10, 19),
    )
    pet.add_task(completed)
    pet.add_task(one_time_future)
    owner = Owner("Jordan", pets=[pet])

    schedule = Scheduler().generate_schedule(owner, date(2026, 10, 18))

    assert schedule == []


def test_weekly_tasks_are_due_only_on_configured_weekdays() -> None:
    monday = date(2026, 10, 19)
    task = make_task(
        "Weekly medication",
        5,
        frequency=Frequency.WEEKLY,
        days_of_week={monday.weekday()},
    )

    assert task.is_due_on(monday)
    assert not task.is_due_on(date(2026, 10, 20))


def test_recurring_task_completion_applies_to_one_date_only() -> None:
    task = make_task("Daily medication", 5)
    task.mark_complete(date(2026, 10, 18))

    assert not task.is_due_on(date(2026, 10, 18))
    assert task.is_due_on(date(2026, 10, 19))


def test_invalid_task_duration_is_rejected() -> None:
    with pytest.raises(ValueError, match="duration"):
        make_task("Walk", 0)


def test_task_management_targets_the_selected_pet_and_id() -> None:
    pet = Pet("Mochi", "dog", 3)
    owner = Owner("Jordan", pets=[pet])
    task = make_task("Walk", 20)
    owner.add_task(pet.id, task)

    removed = owner.remove_task(pet.id, task.id)

    assert removed is task
    assert owner.get_all_tasks() == []


def test_scheduler_marks_task_complete_across_all_pets() -> None:
    pet = Pet("Mochi", "dog", 3)
    task = make_task("Medication", 5)
    pet.add_task(task)
    owner = Owner("Jordan", pets=[pet])

    Scheduler().mark_task_complete(owner, task.id, date(2026, 10, 18))

    assert not task.is_due_on(date(2026, 10, 18))
    assert task.is_due_on(date(2026, 10, 19))
