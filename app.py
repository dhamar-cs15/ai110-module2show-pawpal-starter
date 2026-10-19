"""Streamlit interface for managing pets and generating care schedules."""

from datetime import date, time

import streamlit as st

from pawpal_system import Frequency, Owner, Pet, Scheduler, Task


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler()

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

st.title("🐾 PawPal+")
st.markdown(
    """
PawPal+ helps you keep track of care tasks across your pets and build a
priority-based daily task list.
"""
)

owner.name = st.text_input("Owner name", value=owner.name)
owner.time_availability_minutes = st.number_input(
    "Available care time today (minutes)",
    min_value=0,
    max_value=1440,
    value=owner.time_availability_minutes,
)
plan_date = st.date_input("Plan date", value=date.today())

st.divider()
st.subheader("Your pets")

with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_age = st.number_input("Age (years)", min_value=0, max_value=100, value=1)
    add_pet_submitted = st.form_submit_button("Add pet")

if add_pet_submitted:
    if not pet_name.strip():
        st.error("Enter a name for the pet.")
    else:
        pet = Pet(name=pet_name.strip(), species=species, age=int(pet_age))
        owner.add_pet(pet)
        st.success(f"Added {pet.name}.")

if owner.pets:
    st.dataframe(
        [
            {"Pet": pet.name, "Species": pet.species, "Age": pet.age}
            for pet in owner.pets
        ],
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("Add a pet before creating care tasks.")

st.divider()
st.subheader("Care tasks")

if owner.pets:
    pets_by_id = {str(pet.id): pet for pet in owner.pets}
    with st.form("add_task_form", clear_on_submit=True):
        selected_pet_id = st.selectbox(
            "Assign task to",
            options=list(pets_by_id),
            format_func=lambda pet_id: pets_by_id[pet_id].name,
        )
        task_description = st.text_input("Task description")
        duration_minutes = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
        priority_level = st.selectbox(
            "Priority", ["low", "medium", "high"], index=2
        )
        frequency_value = st.selectbox(
            "Frequency",
            [frequency.value for frequency in Frequency],
            format_func=str.capitalize,
        )
        task_time = st.time_input("Preferred start time", value=time(8, 0))
        if frequency_value == Frequency.WEEKLY.value:
            weekdays = st.multiselect(
                "Repeat on",
                options=list(range(7)),
                format_func=lambda weekday: (
                    "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"
                )[weekday],
            )
        else:
            weekdays = []
        add_task_submitted = st.form_submit_button("Add task")

    if add_task_submitted:
        try:
            task = Task(
                description=task_description,
                duration_minutes=int(duration_minutes),
                priority_level=priority_level,
                frequency=Frequency(frequency_value),
                scheduled_time=task_time,
                scheduled_date=(
                    plan_date if frequency_value == Frequency.ONCE.value else None
                ),
                days_of_week=set(weekdays),
            )
            owner.add_task(pets_by_id[selected_pet_id].id, task)
            st.success(f"Added “{task.description}” for {pets_by_id[selected_pet_id].name}.")
        except ValueError as error:
            st.error(str(error))

    pet_names_by_id = {pet.id: pet.name for pet in owner.pets}
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.dataframe(
            [
                {
                    "Pet": pet_names_by_id[task.pet_id],
                    "Task": task.description,
                    "Time": (
                        task.scheduled_time.strftime("%H:%M")
                        if task.scheduled_time
                        else "Not set"
                    ),
                    "Duration (min)": task.duration_minutes,
                    "Priority": task.priority_level,
                    "Frequency": task.frequency.value,
                }
                for task in all_tasks
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No care tasks yet. Add one above.")

st.divider()
st.subheader("Today's schedule")
st.caption(
    "Tasks are selected across all your pets by priority and available minutes. "
    "Overlapping fixed-time tasks are flagged below."
)

if st.button("Generate schedule"):
    schedule = scheduler.generate_schedule(owner, plan_date)
    if schedule:
        for task in schedule:
            pet_name_for_task = pet_names_by_id[task.pet_id]
            task_time_label = (
                task.scheduled_time.strftime("%H:%M")
                if task.scheduled_time
                else "Time not set"
            )
            st.write(
                f"**{task_time_label} — {task.description}** for {pet_name_for_task} "
                f"({task.duration_minutes} min; {task.priority_level} priority)"
            )
        conflict_warning = scheduler.get_time_conflict_warning(schedule)
        if conflict_warning:
            st.warning(conflict_warning)
    else:
        st.info("No due tasks fit within the available time for this date.")
