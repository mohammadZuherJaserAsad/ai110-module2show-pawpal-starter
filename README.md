# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## Features

### Core System
- **Owner & Pet Management**: Register multiple pets under an owner, each with their own task lists
- **Task Tracking**: Create care tasks with description, time, duration, priority, and frequency

### Smarter Scheduling
- **Sorting by Time**: Tasks are automatically sorted chronologically so owners can follow a timeline
- **Priority Sorting**: High-priority tasks (medications, vet visits) are surfaced first
- **Filtering**: View tasks by specific pet or by completion status
- **Conflict Detection**: The system warns when two tasks are scheduled at the same time
- **Recurring Tasks**: Daily and weekly tasks automatically regenerate after completion using Python's `timedelta`

### Streamlit UI
- Interactive forms for adding pets and scheduling tasks
- Color-coded priority indicators (🔴 High, 🟡 Medium, 🟢 Low)
- Real-time conflict warnings
- Summary metrics (tasks completed, time remaining, high-priority count)
- One-click task completion with automatic recurrence handling

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

### Run the CLI Demo

```bash
python main.py
```

### Run the Streamlit App

```bash
streamlit run app.py
```

### Testing PawPal+

Run the automated test suite with:

```bash
python -m pytest
```

The test suite covers:
- Task completion and status changes
- Task addition and pet name assignment
- Chronological sorting correctness
- Priority-based sorting (high > medium > low)
- Daily and weekly recurrence logic
- Conflict detection (same-pet and cross-pet)
- Edge cases (empty tasks, non-existent pets, one-time tasks)

**Confidence Level**: ⭐⭐⭐⭐ (4/5) — All 24 tests pass covering core behaviors and key edge cases.

## System Architecture

The system follows a modular OOP design with four core classes:

| Class | Responsibility |
|-------|---------------|
| `Task` | Dataclass representing a single care activity |
| `Pet` | Stores pet info and manages its task list |
| `Owner` | Manages multiple pets and aggregates tasks |
| `Scheduler` | The "brain" — sorts, filters, detects conflicts, handles recurrence |

See `uml_diagram.mermaid` for the full class diagram, or paste it into the [Mermaid Live Editor](https://mermaid.live) to visualize.
