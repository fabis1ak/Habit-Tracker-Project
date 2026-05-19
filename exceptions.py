class HabitTrackerError(Exception):
    """Bazowy wyjątek dla naszej aplikacji."""
    pass

class InvalidGoalError(HabitTrackerError):
    """Zgłaszany, gdy cel lub limit jest nieprawidłowy (np. ujemne kalorie)."""
    pass

class InvalidDateError(HabitTrackerError):
    """Zgłaszany, gdy format daty nie przejdzie walidacji regexem."""
    pass