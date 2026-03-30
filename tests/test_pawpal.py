"""
Automated Test Suite for PawPal+ System
Covers core behaviors: task management, sorting, filtering,
conflict detection, and recurring task handling.
"""

import pytest
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# --- Fixtures ---

@pytest.fixture
def today():
    return datetime.now().strftime("%Y-%m-%d")


@pytest.fixture
def sample_owner(today):
    owner = Owner(name="TestOwner")
    dog = Pet(name="Rex", species="dog", age=4)
    cat = Pet(name="Luna", species="cat", age=2)

    dog.add_task(Task(description="Morning walk", time="07:00", priority="high", frequency="daily", date=today))
    dog.add_task(Task(description="Evening walk", time="18:00", priority="medium", frequency="daily", date=today))
    dog.add_task(Task(description="Vet appointment", time="10:00", priority="high", frequency="once", date=today))

    cat.add_task(Task(description="Feeding", time="08:00", priority="high", frequency="daily", date=today))
    cat.add_task(Task(description="Playtime", time="15:00", priority="low", frequency="daily", date=today))

    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner


@pytest.fixture
def scheduler(sample_owner):
    return Scheduler(owner=sample_owner)


# --- Task Tests ---

class TestTask:
    def test_mark_complete(self, today):
        """Verify that mark_complete() changes the task's completed status."""
        task = Task(description="Walk", time="09:00", date=today)
        assert task.completed is False
        task.mark_complete()
        assert task.completed is True

    def test_is_due_today(self, today):
        """Verify that is_due_today() correctly identifies today's tasks."""
        task_today = Task(description="Walk", time="09:00", date=today)
        task_tomorrow = Task(description="Walk", time="09:00", date="2099-01-01")
        assert task_today.is_due_today() is True
        assert task_tomorrow.is_due_today() is False

    def test_create_next_occurrence_daily(self, today):
        """Verify daily tasks create a next occurrence for tomorrow."""
        task = Task(description="Walk", time="07:00", frequency="daily", pet_name="Rex", date=today)
        next_task = task.create_next_occurrence()
        assert next_task is not None
        expected_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert next_task.date == expected_date
        assert next_task.completed is False
        assert next_task.description == "Walk"

    def test_create_next_occurrence_weekly(self, today):
        """Verify weekly tasks create a next occurrence for next week."""
        task = Task(description="Grooming", time="10:00", frequency="weekly", pet_name="Luna", date=today)
        next_task = task.create_next_occurrence()
        assert next_task is not None
        expected_date = (datetime.now() + timedelta(weeks=1)).strftime("%Y-%m-%d")
        assert next_task.date == expected_date

    def test_create_next_occurrence_once(self, today):
        """Verify one-time tasks do NOT create a next occurrence."""
        task = Task(description="Vet visit", time="10:00", frequency="once", date=today)
        assert task.create_next_occurrence() is None

    def test_task_string_representation(self, today):
        """Verify the string output of a task is readable."""
        task = Task(description="Walk", time="07:00", priority="high", pet_name="Rex", date=today)
        result = str(task)
        assert "Walk" in result
        assert "07:00" in result
        assert "Pending" in result


# --- Pet Tests ---

class TestPet:
    def test_add_task(self, today):
        """Verify adding a task increases the pet's task count."""
        pet = Pet(name="Rex", species="dog")
        assert len(pet.tasks) == 0
        pet.add_task(Task(description="Walk", time="09:00", date=today))
        assert len(pet.tasks) == 1

    def test_add_task_sets_pet_name(self, today):
        """Verify that adding a task auto-sets the pet_name field."""
        pet = Pet(name="Rex", species="dog")
        task = Task(description="Walk", time="09:00", date=today)
        pet.add_task(task)
        assert task.pet_name == "Rex"

    def test_remove_task(self, today):
        """Verify removing a task by description works."""
        pet = Pet(name="Rex", species="dog")
        pet.add_task(Task(description="Walk", time="09:00", date=today))
        assert pet.remove_task("Walk") is True
        assert len(pet.tasks) == 0

    def test_remove_nonexistent_task(self):
        """Verify removing a task that doesn't exist returns False."""
        pet = Pet(name="Rex", species="dog")
        assert pet.remove_task("Nonexistent") is False

    def test_get_pending_tasks(self, today):
        """Verify filtering for pending (incomplete) tasks."""
        pet = Pet(name="Rex", species="dog")
        t1 = Task(description="Walk", time="09:00", date=today)
        t2 = Task(description="Feed", time="10:00", date=today)
        t2.mark_complete()
        pet.add_task(t1)
        pet.add_task(t2)
        pending = pet.get_pending_tasks()
        assert len(pending) == 1
        assert pending[0].description == "Walk"


# --- Owner Tests ---

class TestOwner:
    def test_add_pet(self):
        """Verify adding a pet to an owner."""
        owner = Owner(name="Jordan")
        owner.add_pet(Pet(name="Rex", species="dog"))
        assert len(owner.pets) == 1

    def test_get_all_tasks(self, sample_owner):
        """Verify retrieving all tasks across all pets."""
        all_tasks = sample_owner.get_all_tasks()
        assert len(all_tasks) == 5  # 3 for Rex + 2 for Luna

    def test_get_pet(self, sample_owner):
        """Verify finding a pet by name."""
        pet = sample_owner.get_pet("Rex")
        assert pet is not None
        assert pet.name == "Rex"

    def test_get_pet_not_found(self, sample_owner):
        """Verify None is returned for a non-existent pet."""
        assert sample_owner.get_pet("Ghost") is None


# --- Scheduler Tests ---

class TestScheduler:
    def test_sort_by_time(self, scheduler, today):
        """Verify tasks are returned in chronological order."""
        tasks = scheduler.owner.get_all_tasks()
        sorted_tasks = scheduler.sort_by_time(tasks)
        times = [t.time for t in sorted_tasks]
        assert times == sorted(times)

    def test_sort_by_priority(self, scheduler):
        """Verify tasks are sorted high > medium > low."""
        tasks = scheduler.owner.get_all_tasks()
        sorted_tasks = scheduler.sort_by_priority(tasks)
        priorities = [t.priority for t in sorted_tasks]
        priority_order = {"high": 0, "medium": 1, "low": 2}
        values = [priority_order[p] for p in priorities]
        assert values == sorted(values)

    def test_filter_by_pet(self, scheduler):
        """Verify filtering tasks by pet name."""
        all_tasks = scheduler.owner.get_all_tasks()
        rex_tasks = scheduler.filter_by_pet(all_tasks, "Rex")
        assert len(rex_tasks) == 3
        assert all(t.pet_name == "Rex" for t in rex_tasks)

    def test_filter_by_status(self, scheduler, today):
        """Verify filtering tasks by completion status."""
        all_tasks = scheduler.owner.get_all_tasks()
        all_tasks[0].mark_complete()
        pending = scheduler.filter_by_status(all_tasks, completed=False)
        completed = scheduler.filter_by_status(all_tasks, completed=True)
        assert len(pending) == 4
        assert len(completed) == 1

    def test_detect_conflicts_same_pet(self, today):
        """Verify conflict detection for same pet with overlapping times."""
        owner = Owner(name="Test")
        pet = Pet(name="Rex", species="dog")
        pet.add_task(Task(description="Walk", time="09:00", date=today))
        pet.add_task(Task(description="Feed", time="09:00", date=today))
        owner.add_pet(pet)

        scheduler = Scheduler(owner=owner)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) == 1
        assert "Conflict" in conflicts[0]

    def test_detect_conflicts_different_pets(self, today):
        """Verify overlap detection across different pets."""
        owner = Owner(name="Test")
        dog = Pet(name="Rex", species="dog")
        cat = Pet(name="Luna", species="cat")
        dog.add_task(Task(description="Walk", time="09:00", date=today))
        cat.add_task(Task(description="Feed", time="09:00", date=today))
        owner.add_pet(dog)
        owner.add_pet(cat)

        scheduler = Scheduler(owner=owner)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) == 1
        assert "overlap" in conflicts[0].lower()

    def test_no_conflicts(self, today):
        """Verify no conflicts when tasks have different times."""
        owner = Owner(name="Test")
        pet = Pet(name="Rex", species="dog")
        pet.add_task(Task(description="Walk", time="07:00", date=today))
        pet.add_task(Task(description="Feed", time="09:00", date=today))
        owner.add_pet(pet)

        scheduler = Scheduler(owner=owner)
        conflicts = scheduler.detect_conflicts()
        assert len(conflicts) == 0

    def test_handle_recurring_daily(self, today):
        """Verify that completing a daily task creates a new one for tomorrow."""
        owner = Owner(name="Test")
        pet = Pet(name="Rex", species="dog")
        task = Task(description="Walk", time="07:00", frequency="daily", date=today)
        pet.add_task(task)
        owner.add_pet(pet)

        scheduler = Scheduler(owner=owner)
        new_task = scheduler.mark_task_complete(task)

        assert task.completed is True
        assert new_task is not None
        assert new_task.completed is False
        assert len(pet.tasks) == 2  # original + new occurrence

    def test_handle_recurring_once(self, today):
        """Verify that completing a one-time task does NOT create a new one."""
        owner = Owner(name="Test")
        pet = Pet(name="Rex", species="dog")
        task = Task(description="Vet", time="10:00", frequency="once", date=today)
        pet.add_task(task)
        owner.add_pet(pet)

        scheduler = Scheduler(owner=owner)
        new_task = scheduler.mark_task_complete(task)

        assert task.completed is True
        assert new_task is None
        assert len(pet.tasks) == 1

    def test_get_todays_schedule(self, scheduler):
        """Verify today's schedule returns sorted tasks."""
        schedule = scheduler.get_todays_schedule()
        assert len(schedule) > 0
        # Should be sorted by priority first
        priority_order = {"high": 0, "medium": 1, "low": 2}
        values = [priority_order[t.priority] for t in schedule]
        assert values == sorted(values)
