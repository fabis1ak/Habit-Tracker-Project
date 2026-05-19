from exceptions import InvalidGoalError

class Habit:
    def __init__(self, name):
        self.name = name
        self.history = {}

    def log_progress(self, date, value):
        self.history[date] = value

    def to_dict(self):
        return {"type": self.__class__.__name__, "name": self.name, "history": self.history}

class LimitHabit(Habit):
    def __init__(self, name, limit):
        super().__init__(name)
        if limit <= 0:
            raise InvalidGoalError("Limit musi być większy od zera.")
        self.limit = limit
        
    def to_dict(self):
        data = super().to_dict()
        data["limit"] = self.limit
        return data

class BinaryHabit(Habit):
    def log_progress(self, date, completed: bool):
        super().log_progress(date, completed)

#  dla jednorazowych zadań 
class Task:
    def __init__(self, description, is_done=False):
        self.description = description
        self.is_done = is_done

    def to_dict(self):
        return {"description": self.description, "is_done": self.is_done}

class AppManager:
    def __init__(self):
        self.habits = []
        self.tasks = [] # Dodana lista na taski

    def add_habit(self, habit: Habit):
        self.habits.append(habit)
        
    def add_task(self, task: Task):
        self.tasks.append(task)

    def get_habit_names(self):
        return [habit.name for habit in self.habits]

    def sort_habits(self):
        self.habits = sorted(self.habits, key=lambda h: h.name.lower())