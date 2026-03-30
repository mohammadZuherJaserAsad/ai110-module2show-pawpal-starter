"""
PawPal+ System - Core Logic Layer
A smart pet care management system that helps owners keep their pets happy and healthy.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class Task:
    """Represents a single pet care task (feeding, walk, medication, etc.)."""

    description: str
    time: str  # Format: "HH:MM"
    duration_minutes: int = 30
    priority: str = "medium"  # "low", "medium", "high"
    frequency: str = "once"  # "once", "daily", "weekly"
    completed: bool = False
    pet_name: str = ""
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def is_due_today(self) -> bool:
        """Check if this task is due today."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.date == today

    def create_next_occurrence(self) -> Optional["Task"]:
        """Create the next occurrence of a recurring task.

        Daily tasks get rescheduled to tomorrow.
        Weekly tasks get rescheduled to next week.
        One-time tasks return None.
        """
        if self.frequency == "daily":
            next_date = datetime.strptime(self.date, "%Y-%m-%d") + timedelta(days=1)
            return Task(
                description=self.description,
                time=self.time,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                frequency=self.frequency,
                completed=False,
                pet_name=self.pet_name,
                date=next_date.strftime("%Y-%m-%d"),
            )
        elif self.frequency == "weekly":
            next_date = datetime.strptime(self.date, "%Y-%m-%d") + timedelta(weeks=1)
            return Task(
                description=self.description,
                time=self.time,
                duration_minutes=self.duration_minutes,
                priority=self.priority,
                frequency=self.frequency,
                completed=False,
                pet_name=self.pet_name,
                date=next_date.strftime("%Y-%m-%d"),
            )
        return None

    def __str__(self) -> str:
        status = "Done" if self.completed else "Pending"
        return (
            f"[{status}] {self.time} - {self.description} "
            f"({self.pet_name}, {self.priority} priority, {self.duration_minutes}min)"
        )


@dataclass
class Pet:
    """Represents a pet with its details and associated tasks."""

    name: str
    species: str
    age: int = 1
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a care task for this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_description: str) -> bool:
        """Remove a task by its description. Returns True if found and removed."""
        for i, task in enumerate(self.tasks):
            if task.description == task_description:
                self.tasks.pop(i)
                return True
        return False

    def get_pending_tasks(self) -> list:
        """Get all incomplete tasks for this pet."""
        return [t for t in self.tasks if not t.completed]

    def __str__(self) -> str:
        return f"{self.name} ({self.species}, age {self.age}) - {len(self.tasks)} tasks"


@dataclass
class Owner:
    """Represents a pet owner who manages multiple pets."""

    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Register a new pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name. Returns True if found and removed."""
        for i, pet in enumerate(self.pets):
            if pet.name == pet_name:
                self.pets.pop(i)
                return True
        return False

    def get_all_tasks(self) -> list:
        """Retrieve all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Find a pet by name."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def __str__(self) -> str:
        pet_names = ", ".join(p.name for p in self.pets) if self.pets else "No pets"
        return f"Owner: {self.name} | Pets: {pet_names}"


class Scheduler:
    """The brain of PawPal+ — retrieves, organizes, and manages tasks across pets.

    Handles sorting by time/priority, filtering, conflict detection,
    and recurring task management.
    """

    def __init__(self, owner: Owner):
        """Initialize the scheduler with an owner."""
        self.owner = owner

    def get_todays_schedule(self) -> list:
        """Get all tasks due today, sorted by priority then time."""
        all_tasks = self.owner.get_all_tasks()
        today_tasks = [t for t in all_tasks if t.is_due_today()]
        return self.sort_by_priority(self.sort_by_time(today_tasks))

    def sort_by_time(self, tasks: list) -> list:
        """Sort tasks chronologically by their scheduled time (HH:MM format).

        Uses a lambda key to compare time strings, which works because
        HH:MM format is naturally sortable as strings.
        """
        return sorted(tasks, key=lambda t: t.time)

    def sort_by_priority(self, tasks: list) -> list:
        """Sort tasks by priority (high > medium > low).

        Tasks with the same priority retain their relative order (stable sort).
        """
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(tasks, key=lambda t: priority_order.get(t.priority, 1))

    def filter_by_pet(self, tasks: list, pet_name: str) -> list:
        """Filter tasks to only include those belonging to a specific pet."""
        return [t for t in tasks if t.pet_name == pet_name]

    def filter_by_status(self, tasks: list, completed: bool = False) -> list:
        """Filter tasks by their completion status."""
        return [t for t in tasks if t.completed == completed]

    def detect_conflicts(self, tasks: list = None) -> list:
        """Detect scheduling conflicts where two tasks overlap in time.

        Checks if any two tasks for the same pet are scheduled at the same time.
        Returns a list of warning messages describing each conflict.

        Tradeoff: Only checks for exact time matches rather than overlapping
        durations, which keeps the logic simple and fast.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()

        conflicts = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                if tasks[i].time == tasks[j].time and not tasks[i].completed and not tasks[j].completed:
                    if tasks[i].pet_name == tasks[j].pet_name:
                        conflicts.append(
                            f"Conflict for {tasks[i].pet_name}: "
                            f"'{tasks[i].description}' and '{tasks[j].description}' "
                            f"are both scheduled at {tasks[i].time}"
                        )
                    else:
                        conflicts.append(
                            f"Time overlap: '{tasks[i].description}' ({tasks[i].pet_name}) "
                            f"and '{tasks[j].description}' ({tasks[j].pet_name}) "
                            f"are both at {tasks[i].time}"
                        )
        return conflicts

    def handle_recurring(self, task: Task) -> Optional[Task]:
        """Handle a recurring task after completion.

        When a daily or weekly task is marked complete, this method
        creates the next occurrence and adds it to the appropriate pet.
        Returns the new task if created, or None for one-time tasks.
        """
        next_task = task.create_next_occurrence()
        if next_task is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet:
                pet.add_task(next_task)
        return next_task

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Mark a task complete and handle recurrence if applicable."""
        task.mark_complete()
        return self.handle_recurring(task)

    def get_schedule_summary(self) -> str:
        """Generate a formatted summary of today's schedule."""
        schedule = self.get_todays_schedule()
        conflicts = self.detect_conflicts(schedule)

        lines = []
        lines.append(f"=== Today's Schedule for {self.owner.name} ===")
        lines.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        lines.append(f"Total tasks: {len(schedule)}")
        lines.append("")

        if conflicts:
            lines.append("*** WARNINGS ***")
            for c in conflicts:
                lines.append(f"  ! {c}")
            lines.append("")

        if not schedule:
            lines.append("No tasks scheduled for today.")
        else:
            current_pet = ""
            for task in schedule:
                if task.pet_name != current_pet:
                    current_pet = task.pet_name
                    lines.append(f"--- {current_pet} ---")
                lines.append(f"  {task}")

        return "\n".join(lines)
