# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial UML design included four core classes:

- **Owner**: Represents the pet owner. Responsible for managing a list of Pet objects. It can add/remove pets and retrieve all tasks across all pets. This is the top-level container that the Scheduler accesses to get pet data.

- **Pet**: Represents an individual pet (dog, cat, etc.) with attributes like name, species, and age. Each Pet holds a list of Task objects. It can add/remove tasks and filter for pending (incomplete) tasks.

- **Task**: A dataclass representing a single care activity (walk, feeding, medication, etc.). Attributes include description, scheduled time, duration, priority level, frequency (once/daily/weekly), and completion status. It can mark itself complete and generate the next occurrence for recurring tasks.

- **Scheduler**: The "brain" of the system. It takes an Owner and orchestrates all task management — sorting tasks by time or priority, filtering by pet or status, detecting scheduling conflicts, and handling recurring task generation when tasks are completed.

The relationships are: Owner has many Pets (1-to-many), each Pet has many Tasks (1-to-many), and the Scheduler manages one Owner (1-to-1).

**b. Design changes**

During implementation, I made several changes:

1. **Added a `date` field to Task**: The original skeleton didn't account for dates, only times. I added a date field so the Scheduler could filter for "today's tasks" and properly handle recurring tasks by calculating the next date using `timedelta`.

2. **Added `mark_task_complete` to Scheduler**: Initially, marking a task complete and handling recurrence were separate steps. I combined them into a single Scheduler method so the UI only needs one call to complete a task and auto-generate the next occurrence.

3. **Added `get_schedule_summary` to Scheduler**: This wasn't in the original UML but became necessary for the CLI demo to produce readable output.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

My scheduler considers three main constraints:

- **Priority** (high > medium > low): High-priority tasks like medications or vet appointments appear first in the schedule.
- **Time**: Tasks are sorted chronologically so the owner can follow a timeline for their day.
- **Frequency**: The system distinguishes between one-time, daily, and weekly tasks. When a recurring task is completed, the next occurrence is automatically created.

I decided priority should take precedence over time in the final sorted schedule, because a high-priority medication at 10:00 AM is more important to highlight than a low-priority playtime at 9:00 AM.

**b. Tradeoffs**

One key tradeoff is in conflict detection: my Scheduler only checks for **exact time matches** rather than checking if task durations overlap. For example, a 45-minute walk starting at 9:00 and a feeding at 9:30 would not be flagged as a conflict, even though they overlap in practice.

This tradeoff is reasonable because:
- It keeps the detection algorithm simple and fast (O(n²) comparisons on time strings)
- Most pet care tasks are short, so exact conflicts are the most common real-world issue
- Adding duration-based overlap detection would add complexity without much practical benefit for a typical daily schedule

---

## 3. AI Collaboration

**a. How you used AI**

I used AI tools throughout this project in several ways:

- **Design brainstorming**: I described the pet care scenario and asked AI to suggest the main classes, their attributes, and relationships. This helped me quickly converge on the Owner-Pet-Task-Scheduler architecture.
- **Mermaid UML generation**: I provided my class descriptions and AI generated the Mermaid.js class diagram syntax, which I then refined.
- **Code scaffolding**: AI generated the initial dataclass skeletons based on the UML, which I then fleshed out with actual logic.
- **Test generation**: I asked AI to generate pytest tests covering happy paths and edge cases, then reviewed and adjusted them.
- **Debugging**: When sorting wasn't working correctly, I shared the code and AI identified that I needed a stable sort to maintain time ordering within priority groups.

The most helpful prompts were specific ones like "How should the Scheduler retrieve all tasks from the Owner's pets?" rather than vague ones like "write me a scheduler."

**b. Judgment and verification**

One moment where I didn't accept an AI suggestion was when it proposed using a complex priority queue (heap) for task scheduling. While technically more efficient, it made the code much harder to read and was overkill for a system managing at most 20-30 daily tasks. I kept the simpler `sorted()` approach with lambda keys, which is more readable and perfectly performant for this scale.

I verified this by running the demo script with various task configurations and checking that the output matched my expectations for sorting order.

---

## 4. Testing and Verification

**a. What you tested**

My test suite covers these core behaviors:

- **Task completion**: Verifying that `mark_complete()` changes the status from False to True
- **Task addition**: Confirming that adding a task to a Pet increases the task count and correctly sets the pet_name
- **Sorting correctness**: Ensuring tasks are returned in chronological order by time, and in priority order (high > medium > low)
- **Recurrence logic**: Confirming that marking a daily task complete creates a new task for the following day, and that one-time tasks don't recur
- **Conflict detection**: Verifying that the Scheduler flags tasks with the same time (both same-pet and cross-pet conflicts)
- **Edge cases**: Pets with no tasks, removing non-existent tasks, finding non-existent pets

These tests are important because they validate the core scheduling logic that the entire UI depends on. If sorting or conflict detection is broken, the user sees wrong information.

**b. Confidence**

I'm confident at a **4/5 stars** level that the scheduler works correctly for typical use cases. All 24 tests pass, covering the main happy paths and several edge cases.

If I had more time, I'd test:
- Tasks spanning midnight (e.g., an 11:30 PM task with 60-minute duration)
- Very large numbers of tasks (performance testing)
- Tasks with identical descriptions but different pets
- Date edge cases around month/year boundaries for recurring tasks

---

## 5. Reflection

**a. What went well**

I'm most satisfied with the clean separation between the logic layer (`pawpal_system.py`) and the UI layer (`app.py`). Building and testing everything via the CLI demo first meant that when I connected the Streamlit UI, the backend was already solid. The "CLI-first" approach saved a lot of debugging time.

**b. What you would improve**

If I had another iteration, I would:
- Add duration-based conflict detection (not just exact time matches)
- Implement data persistence with JSON so pets and tasks survive between sessions
- Add a "weekly view" in addition to the daily schedule
- Improve the Scheduler's sorting to support custom sort orders chosen by the user

**c. Key takeaway**

The most important thing I learned is that when collaborating with AI, you need to be the "architect" — AI is great at generating code quickly, but the human needs to make the design decisions. For example, choosing a simple `sorted()` over a heap, or deciding that exact-time conflict detection is sufficient. AI gives you options; your job is to evaluate which option fits your specific scenario.
