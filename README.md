# Habit & Task Tracker

A desktop productivity app built with Python and Tkinter that helps you build habits, manage tasks, and track your daily progress — all stored locally in a JSON file.

---

## Features

### Habits
- **Binary habits** — track daily yes/no activities (e.g. meditation, workout)
- **Quantitative habits** — track measurable goals with a daily target (e.g. 2 L of water, 2500 kcal)
- **Streak counter** — see how many consecutive days you've hit your goal
- **30-day completion rate** — visualized with a progress bar in the Statistics tab
- **Progress bar** — for quantitative habits, see today's value vs. target at a glance
- **Full history view** — inspect every logged entry per habit
- **Delete habits** — remove a habit and its entire history

### Tasks (To-Do)
- **Priority levels** — High / Medium / Low, color-coded
- **Due dates** — optional deadline per task (YYYY-MM-DD)
- **Overdue detection** — tasks past their deadline are highlighted in red
- **Filters** — view All / Pending / Done tasks
- **Mark as done** — one click to complete a task
- **Delete & bulk clear** — remove individual tasks or wipe all completed ones at once

### Statistics
- Summary cards: total habits, completed tasks, best streak, average completion rate
- Per-habit breakdown: streak, 30-day completion rate with a progress bar
- Overdue task list

### Tools
- **TDEE Calculator** — Mifflin-St Jeor formula with activity multiplier; result can be added as a habit instantly
- **CSV Export** — export your full habit history to `habits_export.csv`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| GUI | Tkinter + ttk (built-in) |
| Storage | JSON (local file) |
| Architecture | OOP — models, storage, utils, exceptions |

No external dependencies required.

---

## Project Structure

```
HabitTrackerProject/
├── main.py          # GUI — all windows, tabs, dialogs
├── models.py        # Habit, LimitHabit, BinaryHabit, Task, AppManager
├── storage.py       # JSON save/load (DataStorage)
├── utils.py         # Date validation, TDEE calculation, generators
├── exceptions.py    # Custom exception hierarchy
└── data.json        # Auto-created on first save
```

---

## Getting Started

**Requirements:** Python 3.10 or newer (Tkinter is included in the standard library).

```bash
git clone https://github.com/fabis1ak/HabitTrackerProject.git
cd HabitTrackerProject
python main.py
```

No `pip install` needed.

---

## Usage

1. **Add a habit** — click `+ Dodaj nawyk`, choose Binary or Quantitative, enter a name (and daily target if quantitative).
2. **Log progress** — select a habit and click `Zaloguj postęp`. Today's date is pre-filled.
3. **Check your streaks** — the Habits tab shows the current streak and 30-day rate for each habit.
4. **Add tasks** — switch to the Zadania tab, click `+ Dodaj zadanie`, set priority and an optional due date.
5. **View statistics** — the Statystyki tab shows a full overview with per-habit progress bars.
6. **Calculate calories** — go to Narzędzia, fill in the TDEE form, and optionally add the result as a habit.
7. **Export data** — click `Eksportuj nawyki do CSV` to get a spreadsheet-ready file.

---

## Data Storage

All data is saved automatically in `data.json` in the same directory as the script. The file is updated after every action — no manual save needed.

---

## License

MIT — free to use and modify.
