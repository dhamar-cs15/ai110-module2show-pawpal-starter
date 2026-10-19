# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

```
SAMPLE OUTPUT 1:

Today's Schedule — Sunday, October 18, 2026
07:30 — Breakfast for Mochi (10 min, high priority)
08:00 — Morning walk for Mochi (30 min, high priority)
08:15 — Feed Biscuit for Biscuit (5 min, medium priority)
```


## Implementation Summary
PHASE 2
The four main classes have been thoroughly implemented. Task takes care of one activity at a time, keeping track of its duration, priority, frequency, and completion status. Pet stores all the information pertaining the pet itself, and is where all the task methods live, since any task added pertains to one specific pet at a time. Since the task methods live here, when a task is created/edited, it will pull its "template" information from the Task class. 
The Owner class has information about the owner and a list of their pets; this means the owner class will be interacting with the pet class to create instances for each of the pets the owner has. Finally, the Scheduler class retrieveds, filters, and organizes tasks; it's able to do this because it has information from the owner class (such as time preferences) and the pet class (such as tasks already assigned to that pet).

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## Bullet point/paragraph version of Smarter Scheduling section (Phase 4)
Task Sorting
- Methods: Scheduler.organize_tasks()
- What it does: it sorts the tasks by scheduled start time, in chronological order. if there are any tasks that don't have a specified scheduled time, they will go last and be given least priority

Filtering
- Methods: Scheduler.filter_tasks()
- What it does: it can filter the owner's tasks either by pet name, completion status, or both. This allows the program to separate tasks pertaining to only one pet, or all tasks that still need to be done (or both)

Conflict handling:
- Methods: Scheduler.find_time_conflicts(), Scheduler.get_time_conflict_warning()
- What it does: it's able to find the tasks that have a conflict (times overlap) and ignores any tasks that don't have a specified time. if there is a conflict, it makes sure to raise this as a warning so that the user knows that there are tasks trying to be scheduled at the same time 

Recurring task logic:
- Methods: Scheduler.mark_task_complete()
- What it does: If a task is recurring, this feature looks out for when it gets completed. Once it is completed, it creates the next dated occurrence (such as for the next day if daily, or the same day in the next week)


## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
