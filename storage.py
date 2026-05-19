import json
import os
from models import LimitHabit, BinaryHabit, Task, AppManager

class DataStorage:
    def __init__(self, filename="data.json"):
        self.filename = filename

    def save(self, manager: AppManager):
        with open(self.filename, 'w', encoding='utf-8') as file:
            data = {
                "habits": [habit.to_dict() for habit in manager.habits],
                "tasks": [task.to_dict() for task in manager.tasks]
            }
            json.dump(data, file, indent=4)

    def load(self, manager: AppManager):
        if not os.path.exists(self.filename):
            return
            
        with open(self.filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # ładowanie nawyków
        for item in data.get("habits", []):
            if item["type"] == "LimitHabit":
                habit = LimitHabit(item["name"], item["limit"])
            else:
                habit = BinaryHabit(item["name"])
            habit.history = item["history"]
            manager.add_habit(habit)
            
        # ładowanie tasków
        for item in data.get("tasks", []):
            manager.add_task(Task(item["description"], item["is_done"]))