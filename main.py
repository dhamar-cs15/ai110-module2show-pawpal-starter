"""Create sample PawPal+ data and print today's multi-pet schedule."""

from datetime import date, time

from pawpal_system import Frequency, Owner, Pet, Scheduler, Task


def main() -> None:
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
            scheduled_time=time(8, 15),
        ),
    )

    today = date.today()
    scheduler = Scheduler()
    schedule = scheduler.generate_schedule(owner, today)
    pet_names = {pet.id: pet.name for pet in owner.pets}

    print(f"Today's Schedule — {today:%A, %B %d, %Y}")
    if not schedule:
        print("No tasks fit the available time.")
        return

    for task in schedule:
        task_time = task.scheduled_time.strftime("%H:%M") if task.scheduled_time else "Time TBD"
        pet_name = pet_names[task.pet_id]
        print(
            f"{task_time} — {task.description} for {pet_name} "
            f"({task.duration_minutes} min, {task.priority_level} priority)"
        )


if __name__ == "__main__":
    main()
