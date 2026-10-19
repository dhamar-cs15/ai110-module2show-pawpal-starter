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


def test_find_time_conflicts_detects_overlaps_for_same_and_different_pets() -> None:
    mochi = Pet("Mochi", "dog", 3)
    biscuit = Pet("Biscuit", "cat", 5)
    same_pet_first = make_task(
        "Walk", 30, scheduled_time=time(9, 0)
    )
    same_pet_overlap = make_task(
        "Medication", 10, scheduled_time=time(9, 20)
    )
    other_pet_overlap = make_task(
        "Feed Biscuit", 5, scheduled_time=time(9, 25)
    )
    after_overlap = make_task("Play", 15, scheduled_time=time(9, 30))
    for task in (same_pet_first, same_pet_overlap, after_overlap):
        mochi.add_task(task)
    biscuit.add_task(other_pet_overlap)

    conflicts = Scheduler().find_time_conflicts(
        [same_pet_first, same_pet_overlap, other_pet_overlap, after_overlap]
    )

    assert conflicts == [
        (same_pet_first, same_pet_overlap),
        (same_pet_first, other_pet_overlap),
        (same_pet_overlap, other_pet_overlap),
    ]


def test_find_time_conflicts_ignores_untimed_and_adjacent_tasks() -> None:
    first = make_task("Breakfast", 15, scheduled_time=time(8, 0))
    adjacent = make_task("Walk", 30, scheduled_time=time(8, 15))
    untimed = make_task("Grooming", 20)

    assert Scheduler().find_time_conflicts([first, adjacent, untimed]) == []


def test_time_conflict_warning_is_non_fatal_and_describes_overlaps() -> None:
    first = make_task("Morning walk", 30, scheduled_time=time(9, 0))
    second = make_task("Medication", 10, scheduled_time=time(9, 20))
    scheduler = Scheduler()

    warning = scheduler.get_time_conflict_warning([first, second])

    assert warning is not None
    assert "1 time conflict" in warning
    assert "Morning walk" in warning
    assert "Medication" in warning


def test_time_conflict_warning_is_none_when_no_conflicts_exist() -> None:
    first = make_task("Breakfast", 15, scheduled_time=time(8, 0))
    second = make_task("Walk", 30, scheduled_time=time(8, 15))

    assert Scheduler().get_time_conflict_warning([first, second]) is None


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
    scheduler = Scheduler()

    scheduler.mark_task_complete(owner, task.id, date(2026, 10, 18))

    assert not task.is_due_on(date(2026, 10, 18))
    next_task = pet.care_tasks[1]
    assert next_task is not task
    assert next_task.id != task.id
    assert next_task.scheduled_date == date(2026, 10, 19)
    assert next_task.is_due_on(date(2026, 10, 19))

    scheduler.mark_task_complete(owner, next_task.id, date(2026, 10, 19))

    following_task = pet.care_tasks[2]
    assert following_task.scheduled_date == date(2026, 10, 20)
    assert following_task.is_due_on(date(2026, 10, 20))


def test_daily_task_next_occurrence_rolls_over_to_new_year() -> None:
    pet = Pet("Mochi", "dog", 3)
    task = make_task("Medication", 5)
    pet.add_task(task)
    owner = Owner("Jordan", pets=[pet])

    Scheduler().mark_task_complete(owner, task.id, date(2026, 12, 31))

    assert pet.care_tasks[1].scheduled_date == date(2027, 1, 1)


def test_completing_weekly_task_creates_next_configured_weekday() -> None:
    pet = Pet("Mochi", "dog", 3)
    monday = date(2026, 10, 19)
    task = make_task(
        "Weekly medication",
        5,
        frequency=Frequency.WEEKLY,
        days_of_week={0, 2},
    )
    pet.add_task(task)
    owner = Owner("Jordan", pets=[pet])

    Scheduler().mark_task_complete(owner, task.id, monday)

    next_task = pet.care_tasks[1]
    assert next_task.scheduled_date == date(2026, 10, 21)
    assert not next_task.is_due_on(monday)
    assert next_task.is_due_on(date(2026, 10, 21))


def test_recurring_task_cannot_create_duplicate_next_occurrences() -> None:
    pet = Pet("Mochi", "dog", 3)
    task = make_task("Medication", 5)
    pet.add_task(task)
    owner = Owner("Jordan", pets=[pet])
    scheduler = Scheduler()
    completion_date = date(2026, 10, 18)

    scheduler.mark_task_complete(owner, task.id, completion_date)

    with pytest.raises(ValueError, match="already completed"):
        scheduler.mark_task_complete(owner, task.id, completion_date)
    assert len(pet.care_tasks) == 2


def test_filter_tasks_by_completion_status_and_pet_name() -> None:
    mochi = Pet("Mochi", "dog", 3)
    biscuit = Pet("Biscuit", "cat", 5)
    completed = make_task(
        "Medication",
        5,
        frequency=Frequency.ONCE,
        scheduled_date=date(2026, 10, 18),
    )
    incomplete = make_task("Walk", 20)
    other_pet_task = make_task("Feed", 5)
    completed.mark_complete(date(2026, 10, 18))
    mochi.add_task(completed)
    mochi.add_task(incomplete)
    biscuit.add_task(other_pet_task)
    owner = Owner("Jordan", pets=[mochi, biscuit])
    scheduler = Scheduler()

    assert scheduler.filter_tasks(owner, completed=True) == [completed]
    assert scheduler.filter_tasks(owner, completed=False) == [
        incomplete,
        other_pet_task,
    ]
    assert scheduler.filter_tasks(owner, pet_name="mOcHi") == [
        completed,
        incomplete,
    ]
    assert scheduler.filter_tasks(
        owner,
        completed=True,
        pet_name="MOCHI",
    ) == [completed]


def test_filter_tasks_rejects_blank_pet_name() -> None:
    owner = Owner("Jordan")

    with pytest.raises(ValueError, match="Pet name"):
        Scheduler().filter_tasks(owner, pet_name="  ")
