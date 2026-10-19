from datetime import date

from pawpal_system import Frequency, Pet, Task


def test_mark_complete_changes_task_status() -> None:
    task = Task(
        description="Give medication",
        duration_minutes=5,
        priority_level="high",
        frequency=Frequency.ONCE,
        scheduled_date=date.today(),
    )

    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="dog", age=3)
    task = Task(
        description="Morning walk",
        duration_minutes=20,
        priority_level="medium",
    )
    initial_count = len(pet.care_tasks)

    pet.add_task(task)

    assert len(pet.care_tasks) == initial_count + 1
    assert pet.care_tasks[-1] is task