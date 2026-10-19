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

Some of the constraints the scheduler considers are the selected plan date, whether a task is due and incomplete, each task’s duration, the owner’s available minutes, and scheduled start times. It sorts tasks by start time and includes each task if it fits the remaining time budget, through a greedy algorithm. As of now, the scheduler focuses mainly on timing constraints and does not take into account the level of priority each task is assigned, though it does store some of this information. 

I prioritized scheduling tasks that are due on the selected date while respecting the owner’s available time. The priority factor would be a good constraint to consider but I think it would require a different algorithm where the program has to decide which overrules the other: timing or priority. I think with the timing approach, there is a good chance that some of the high priority tasks will be selected, even though it's not guaranteed.


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One algorithm that my scheduler uses is the Greedy algorithm, when it comes to generating the schedule. The algorithm first sorts the tasks by scheduled time and then appends them into the schedule greedily, placing it immediately if it fits within the remaining minutes of our schedule. This is an effective solution because we get as many tasks as possible within our schedule, making sure the time is productive and most tasks get done. The algorithm completes this in O(nlogn) time, which is mainly attributed to the sorting. The tradeoff here, though, is that we're not placing a heavy emphasis on priority levels for the sake of simplicty. The algorithm isn't picking the tasks with aboslute highest priority first, and it's not testing out different combinations of tasks to see which would optimized the schedule the MOST. An algorithm that does account for these factors would add more complexity (which is in itself a tradeoff as well).

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI for the parts in the assignment that suggested to ask the AI chatbot to do a certain thing. Most of implementation process was done by AI. It fleshed out the logic in pawpal_system.py and main.py. I would ask it to explain what it had built and how it worked-- that way I understood it enough to know what the intentions were and if the code actually accomplished those intentions. 

AI was also helpful for the debugging process. I was able to identify when certain features weren't working properly or had edge cases that weren't being considered yet. But trying to find which specific line across multiple files was responsible for a flaw was tricky --- this is where the AI came in handy. It was able to identify which areas needed more work to account for sneaky edge cases. 


**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

There were a couple of things that the AI didn't consider early on that I caught on to but didn't change in case it was addressed later in the assignment. One of these was the overlapping of tasks at the same time; I noticed the first time I ran main.py that one task was scheduled for 8:00 with a duration of 30 minutes but the next task began at 8:15. I prompted the AI for whether this was an accidental flaw in the system design or if it was something we hadn't accounted for yet. While the AI offered some suggestions on how to fix this, I decided to not take any action yet in case it was part of a later phase in the assignment and simply made a note of it for the time being. 

Another instance was when the AI suggested that "One small readability tweak is to track used time instead of subtracting from remaining_minutes." I evaluated the code that the AI suggested and compared it to what I already had for that particular function. I found that the original code was more readable and understandable than the AI's suggestion, which introduced new variables that were only used once and felt redundant. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested that the scheduler retrieves tasks across multiple pets and builds a schedule using tasks due on the selected date. I also tested chronological sorting, including that sorting doesn’t change the original task list. Another thing I had to confirm was conflict detection for overlapping tasks, including tasks with the same start time, and confirmed that untimed or adjacent tasks (such as one that ends exactly at 8:30 and one that starts at 8:30) don’t count as conflicts. 

These tests were important because they make sure the basic functions and features are working before we add anything new. 

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I’m fairly confident that the tested scheduler behaviors work as expected. The tests cover the main scheduling and recurrence cases, but there are edge cases I would expect to not have been considered yet. If I had more time, I’d test an owner with a zero-minute budget, or one where their tasks max out their entire time to see how the system reacts.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I'm most satisfied with the fact that the project works for the most part! The basic system logic is in place and the program doesn't break when performing any of the essential features. It allows the user to add in their information, their pets, and the tasks they need to; it successfully generates a schedule for the day as well.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would want to implement the priority concept if I had more time. I think it would be an interesting thing to try and figure out, especially because it would likely present conflicts with the current algorithm that schedules tasks based on their start times. 

Also, at the beginning the AI suggested creating more classes to separate different functions, but since the assignment only called for 4 classes to include in the design, I only moved forward with the 4 main classes. I think it would be interesting to redesign the system with more classes and see what would change. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Getting started is hard sometimes! It's a bit daunting to see an empty coding file and have very little clue on what to begin writing or what you should even account for. I think having the AI build the skeleton in the early phases was helpful because it provided more structure. I think the UML was also helpful because I was able to see how the different classes worked together visually and that allowed me to understand the project better. Designing systems seems difficult when getting started but AI seems to be helpful in breaking them down into smaller pieces that can be understood individually before they come together to form the larger system. 
