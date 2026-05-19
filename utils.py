import re
from exceptions import InvalidDateError, HabitTrackerError

def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HabitTrackerError as e:
            print(f"\n[BŁĄD APLIKACJI]: {e}")
        except Exception as e:
            print(f"\n[NIEZNANY BŁĄD]: {e}")
    return wrapper

def validate_date(date_str):
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(pattern, date_str):
        raise InvalidDateError("Data musi być w formacie RRRR-MM-DD.")
    return date_str

def habit_history_generator(history_dict):
    for date, value in history_dict.items():
        yield date, value

 # obliczanie kcal 
def calculate_tdee(weight, height, age, gender, activity_level):
    if gender.lower() == 'm':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    elif gender.lower() == 'k':
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    else:
        raise HabitTrackerError("Nieznana płeć. Wybierz 'm' lub 'k'.")
        
    return bmr * activity_level