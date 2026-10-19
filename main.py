"""Create sample PawPal+ data and demonstrate scheduling helpers."""

from datetime import date, time

from pawpal_system import Frequency, Owner, Pet, Scheduler, Task


def print_tasks(tasks: list[Task], pet_names: dict[object, str]) -> None:
    """Print tasks with their scheduled time, pet, and completion state."""
    if not tasks:
        print("No matching tasks.")
        return

    for task in tasks:
        task_time = task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "Time TBD"
        pet_name = pet_names[task.pet_id]
        status = "completed" if task.completed else "incomplete"
        print(
            f"{task_time} — {task.description} for {pet_name} "
            f"({task.duration_minutes} min, {task.priority_level} priority, {status})"
        )


def main() -> None:
    today = date.today()
    owner = Owner(
        name="Jordan",
        preferences="Morning care when possible",
        time_availability_minutes=60,
    )

    dog = Pet(name="Mochi", species="dog", age=3)
    cat = Pet(name="Biscuit", species="cat", age=5)
    owner.add_pet(dog)
    owner.add_pet(cat)

    owner.add_task(
        dog.id,
        Task(
            description="Morning walk",
            duration_minutes=30,
            priority_level="high",
            frequency=Frequency.DAILY,
            scheduled_time=time(8, 0),
        ),
    )
    owner.add_task(
        dog.id,
        Task(
            description="Breakfast",
            duration_minutes=10,
            priority_level="high",
            frequency=Frequency.DAILY,
            scheduled_time=time(7, 30),
        ),
    )
    owner.add_task(
        cat.id,
        Task(
            description="Feed Biscuit",
            duration_minutes=5,
            priority_level="medium",
            frequency=Frequency.DAILY,
            scheduled_time=time(7, 30),
        ),
    )

    completed_task = Task(
        description="Trim nails",
        duration_minutes=15,
        priority_level="low",
        frequency=Frequency.ONCE,
        scheduled_date=today,
    )
    owner.add_task(cat.id, completed_task)
    completed_task.mark_complete(today)

    scheduler = Scheduler()
    schedule = scheduler.generate_schedule(owner, today)
    pet_names = {pet.id: pet.name for pet in owner.pets}

    print(f"Today's Schedule — {today:%A, %B %d, %Y}")
    print_tasks(schedule, pet_names)
    conflict_warning = scheduler.get_time_conflict_warning(schedule)
    if conflict_warning:
        print(f"WARNING: {conflict_warning}")

    print("\nAll tasks sorted by scheduled time:")
    sorted_tasks = scheduler.organize_tasks(owner.get_all_tasks())
    print_tasks(sorted_tasks, pet_names)

    print("\nIncomplete tasks for Mochi:")
    mochi_tasks = scheduler.filter_tasks(
        owner,
        completed=False,
        pet_name="Mochi",
    )
    print_tasks(scheduler.organize_tasks(mochi_tasks), pet_names)

    print("\nCompleted tasks:")
    completed_tasks = scheduler.filter_tasks(owner, completed=True)
    print_tasks(completed_tasks, pet_names)


if __name__ == "__main__":
    main()
