"""
PawPal+ CLI Demo Script
Demonstrates the core functionality of the PawPal+ system.
"""

from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # --- Create an Owner ---
    owner = Owner(name="Mohammed")
    print(f"Created owner: {owner.name}\n")

    # --- Add Pets ---
    buddy = Pet(name="Buddy", species="dog", age=3)
    whiskers = Pet(name="Whiskers", species="cat", age=5)

    owner.add_pet(buddy)
    owner.add_pet(whiskers)
    print(f"Registered pets: {', '.join(p.name for p in owner.pets)}\n")

    # --- Add Tasks (intentionally out of order to test sorting) ---
    today = datetime.now().strftime("%Y-%m-%d")

    buddy.add_task(Task(
        description="Evening walk",
        time="18:00",
        duration_minutes=30,
        priority="medium",
        frequency="daily",
        date=today,
    ))
    buddy.add_task(Task(
        description="Morning walk",
        time="07:00",
        duration_minutes=45,
        priority="high",
        frequency="daily",
        date=today,
    ))
    buddy.add_task(Task(
        description="Flea medication",
        time="09:00",
        duration_minutes=5,
        priority="high",
        frequency="weekly",
        date=today,
    ))
    buddy.add_task(Task(
        description="Afternoon play",
        time="14:00",
        duration_minutes=20,
        priority="low",
        frequency="daily",
        date=today,
    ))

    whiskers.add_task(Task(
        description="Morning feeding",
        time="07:30",
        duration_minutes=10,
        priority="high",
        frequency="daily",
        date=today,
    ))
    whiskers.add_task(Task(
        description="Litter box cleaning",
        time="09:00",
        duration_minutes=10,
        priority="medium",
        frequency="daily",
        date=today,
    ))
    whiskers.add_task(Task(
        description="Grooming session",
        time="14:00",
        duration_minutes=15,
        priority="low",
        frequency="weekly",
        date=today,
    ))

    # --- Create Scheduler and show today's schedule ---
    scheduler = Scheduler(owner=owner)

    print("=" * 50)
    print(scheduler.get_schedule_summary())
    print("=" * 50)

    # --- Demonstrate conflict detection ---
    print("\n--- Conflict Detection ---")
    all_tasks = owner.get_all_tasks()
    conflicts = scheduler.detect_conflicts(all_tasks)
    if conflicts:
        for conflict in conflicts:
            print(f"  Warning: {conflict}")
    else:
        print("  No conflicts detected.")

    # --- Demonstrate sorting ---
    print("\n--- Tasks Sorted by Time ---")
    sorted_tasks = scheduler.sort_by_time(all_tasks)
    for task in sorted_tasks:
        print(f"  {task}")

    # --- Demonstrate filtering ---
    print("\n--- Buddy's Pending Tasks ---")
    buddy_tasks = scheduler.filter_by_pet(all_tasks, "Buddy")
    pending = scheduler.filter_by_status(buddy_tasks, completed=False)
    for task in pending:
        print(f"  {task}")

    # --- Demonstrate task completion + recurring ---
    print("\n--- Completing 'Morning walk' (daily task) ---")
    morning_walk = buddy.tasks[1]  # Morning walk
    new_task = scheduler.mark_task_complete(morning_walk)
    print(f"  Completed: {morning_walk}")
    if new_task:
        print(f"  Next occurrence created: {new_task}")

    # --- Show updated schedule ---
    print(f"\n--- Buddy's Tasks After Completion ---")
    for task in buddy.tasks:
        print(f"  {task}")


if __name__ == "__main__":
    main()
