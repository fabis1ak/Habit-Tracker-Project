import json
import os
from models import LimitHabit, BinaryHabit, Task, AppManager


class DataStorage:
    def __init__(self, filename="data.json"):
        self.filename = filename

    def save(self, manager: AppManager):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump({
                "habits": [h.to_dict() for h in manager.habits],
                "tasks": [t.to_dict() for t in manager.tasks],
            }, f, indent=4, ensure_ascii=False)

    def load(self, manager: AppManager):
        if not os.path.exists(self.filename):
            return
        with open(self.filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for item in data.get("habits", []):
            if item["type"] == "LimitHabit":
                habit = LimitHabit(item["name"], item["limit"])
            else:
                habit = BinaryHabit(item["name"])
            habit.history = item.get("history", {})
            manager.add_habit(habit)

        for item in data.get("tasks", []):
            manager.add_task(Task(
                item["description"],
                item.get("is_done", False),
                item.get("priority", "medium"),
                item.get("due_date"),
            ))
