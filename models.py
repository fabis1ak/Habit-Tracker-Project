from datetime import date, timedelta
from exceptions import InvalidGoalError


class Habit:
    def __init__(self, name):
        self.name = name
        self.history = {}

    def log_progress(self, date_str, value):
        self.history[date_str] = value

    def _is_completed(self, date_str):
        val = self.history.get(date_str)
        return bool(val)

    def streak(self):
        today = date.today()
        count = 0
        for i in range(365):
            d = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if d not in self.history or not self._is_completed(d):
                break
            count += 1
        return count

    def completion_rate(self, days=30):
        today = date.today()
        completed = sum(
            1 for i in range(days)
            if self._is_completed((today - timedelta(days=i)).strftime("%Y-%m-%d"))
        )
        return completed / days * 100

    def to_dict(self):
        return {"type": self.__class__.__name__, "name": self.name, "history": self.history}


class LimitHabit(Habit):
    def __init__(self, name, limit):
        super().__init__(name)
        if limit <= 0:
            raise InvalidGoalError("Limit musi być większy od zera.")
        self.limit = limit

    def _is_completed(self, date_str):
        val = self.history.get(date_str)
        return val is not None and val >= self.limit

    def to_dict(self):
        data = super().to_dict()
        data["limit"] = self.limit
        return data


class BinaryHabit(Habit):
    def log_progress(self, date_str, completed: bool):
        super().log_progress(date_str, completed)


class Task:
    def __init__(self, description, is_done=False, priority="medium", due_date=None):
        self.description = description
        self.is_done = is_done
        self.priority = priority
        self.due_date = due_date

    def to_dict(self):
        return {
            "description": self.description,
            "is_done": self.is_done,
            "priority": self.priority,
            "due_date": self.due_date,
        }


class AppManager:
    def __init__(self):
        self.habits = []
        self.tasks = []

    def add_habit(self, habit):
        self.habits.append(habit)

    def add_task(self, task):
        self.tasks.append(task)

    def delete_habit(self, index):
        self.habits.pop(index)

    def delete_task(self, index):
        self.tasks.pop(index)

    def get_habit_names(self):
        return [habit.name for habit in self.habits]

    def sort_habits(self):
        self.habits = sorted(self.habits, key=lambda h: h.name.lower())
