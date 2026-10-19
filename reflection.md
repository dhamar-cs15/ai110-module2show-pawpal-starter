# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

4 Classes:
- Owner { name, preferences, time availability }
- Pet { name, species, age, preferred tasks/care }
- Tasks/Care { name, category, duration, priority level, scheduled time occurence }
- Daily plan { list of scheduled tasks, date day, duration of tasks, reasoning for plan chosen }

Methods to include: 
- addTask(): allow the user (owner) to add a new task to their schedule
- editTask(): allow the user to edit an existing task (including the duration of it and its priority level)
- removeTask(): allow the user to remove an existing task and all its data
- addPet(): allow user to add a new pet to their application 
- editPet(): allow user to edit any information pertaining to the selected pet
- generatePlan(): create a new daily schedule based on constraints and priorities
- sortTasksByPriority(): sorts the tasks by priority level, ensuring higher priority tasks are first on schedule
- sortTasksByTime(): check which tasks fit into the schedule (after considering priority) and allow tasks that fit to be placed on the schedule
- explainReasoning(): once a schedule is created, explain the reasoning for tasks and order to user



**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The design didn't change much during implementation. I kept the same four classes I decided above in the brainstorming phase. No new methods were added but something interesting that I did notice that the AI did was define the add_pet, edit_pet within the owner class. While these are actions only the owner can do, I think I would have initially thought that the method edit_pet could at least be placed under the Pet class since that's the class that will be holding the data that will be edited. 

Post asking the AI to review my skeleton, changes made:
- the AI identified that the relationship between tasks and pets was unclear. To address this, we implemented a new list in the Pet class, called care_tasks that is a collection of tasks specifically associated with that pet.

- the AI also broke apart the responsibilities assigned to the original class DailyPlan, which took care of both scheduling behavior (such as sorting tasks and figuring out durations) and generating the daily plan. Now, we have a new class called Scheduler, which is responsible for the planning operations while DailyPlan can take care of the result (the finalized plan that's generated)

- the AI also said my definition of scheduled_time was ambiguous (I didn't specify whether it meant a specific time, a range, or a frequency). Therefore, it broke this field into different variables (time_window_start and time_window_end) which can provide more information and are more flexible for use. It also added a new class Recurrence for tasks that occur repeatedly or at certain intervals



---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI for the parts in the assignment that suggested to ask the AI chatbot to do a certain thing. Most of implementation process was done by AI. It fleshed out the logic in pawpal_system.py and main.py. I would ask it to explain what it had built and how it worked-- that way I understood it enough to know what the intentions were and if the code actually accomplished those intentions. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

Schedule inconsistency / conflict management


---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
