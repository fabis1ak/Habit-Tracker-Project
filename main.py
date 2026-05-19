import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import date

from models import AppManager, LimitHabit, BinaryHabit, Task
from storage import DataStorage
from utils import validate_date, calculate_tdee
from exceptions import HabitTrackerError

class HabitTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Habit & Task Tracker")
        self.root.geometry("500x600")
        
        # inicjalizacja bazy danych
        self.manager = AppManager()
        self.storage = DataStorage()
        self.storage.load(self.manager)
        
        self.create_widgets()
        self.refresh_lists()

    def create_widgets(self):
        # tytuł
        tk.Label(self.root, text="Twoje Nawyki", font=("Helvetica", 14, "bold")).pack(pady=5)
        
        # lista nawyków
        self.habits_listbox = tk.Listbox(self.root, height=8, width=50)
        self.habits_listbox.pack(pady=5)
        
        # przyciski dla nawyków
        btn_frame1 = tk.Frame(self.root)
        btn_frame1.pack(pady=5)
        tk.Button(btn_frame1, text="Dodaj Nawyk", command=self.add_habit).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame1, text="Zaloguj Postęp", command=self.log_progress).pack(side=tk.LEFT, padx=5)
        
        # tytuł dla zadań
        tk.Label(self.root, text="Twoje Zadania (To-Do)", font=("Helvetica", 14, "bold")).pack(pady=(15, 5))
        
        # lista zadań
        self.tasks_listbox = tk.Listbox(self.root, height=8, width=50)
        self.tasks_listbox.pack(pady=5)
        
        # przyciski dla zadań
        btn_frame2 = tk.Frame(self.root)
        btn_frame2.pack(pady=5)
        tk.Button(btn_frame2, text="Dodaj Zadanie", command=self.add_task).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame2, text="Oznacz jako zrobione", command=self.complete_task).pack(side=tk.LEFT, padx=5)
        
        # Inne narzędzia
        tk.Label(self.root, text="Narzędzia", font=("Helvetica", 14, "bold")).pack(pady=(15, 5))
        tk.Button(self.root, text="Kalkulator Kalorii (TDEE)", command=self.calc_calories).pack(pady=5)

    def refresh_lists(self):
        """Odświeża widok list na podstawie danych z AppManager."""
        self.habits_listbox.delete(0, tk.END)
        for habit in self.manager.habits:
            if isinstance(habit, LimitHabit):
                self.habits_listbox.insert(tk.END, f"[Ilościowy] {habit.name} (Cel: {habit.limit})")
            else:
                self.habits_listbox.insert(tk.END, f"[Binarny] {habit.name}")
                
        self.tasks_listbox.delete(0, tk.END)
        for task in self.manager.tasks:
            status = "☑" if task.is_done else "☐"
            self.tasks_listbox.insert(tk.END, f"{status} {task.description}")

    def add_habit(self):
        typ = simpledialog.askstring("Typ nawyku", "Wpisz '1' dla ilościowego (np. woda), '2' dla binarnego:")
        if not typ: return
        
        name = simpledialog.askstring("Nazwa", "Podaj nazwę nawyku:")
        if not name: return
        
        try:
            if typ == '1':
                limit = float(simpledialog.askstring("Limit", "Podaj limit (np. 2500):"))
                self.manager.add_habit(LimitHabit(name, limit))
            elif typ == '2':
                self.manager.add_habit(BinaryHabit(name))
            else:
                messagebox.showerror("Błąd", "Nieznany typ nawyku!")
                return
                
            self.manager.sort_habits()
            self.storage.save(self.manager)
            self.refresh_lists()
            messagebox.showinfo("Sukces", "Dodano nawyk!")
        except HabitTrackerError as e:
            messagebox.showerror("Błąd aplikacji", str(e))
        except ValueError:
            messagebox.showerror("Błąd", "Podano nieprawidłową wartość liczbową.")

    def add_task(self):
        desc = simpledialog.askstring("Nowe zadanie", "Co masz do zrobienia?")
        if desc:
            self.manager.add_task(Task(desc))
            self.storage.save(self.manager)
            self.refresh_lists()

    def log_progress(self):
        selection = self.habits_listbox.curselection()
        if not selection:
            messagebox.showwarning("Uwaga", "Wybierz najpierw nawyk z listy!")
            return
            
        idx = selection[0]
        habit = self.manager.habits[idx]
        
    
        dzisiaj = date.today().strftime("%Y-%m-%d")
        data = simpledialog.askstring("Data", "Podaj datę (RRRR-MM-DD):", initialvalue=dzisiaj)
        
        if not data: return
        
        try:
            validate_date(data)
            if isinstance(habit, LimitHabit):
                val = float(simpledialog.askstring("Postęp", f"Podaj wartość (Twój cel to {habit.limit}):"))
                habit.log_progress(data, val)
            else:
                odp = messagebox.askyesno("Postęp", f"Czy wykonałeś dzisiaj '{habit.name}'?")
                habit.log_progress(data, odp)
                
            self.storage.save(self.manager)
            messagebox.showinfo("Sukces", "Zapisano postęp!")
        except HabitTrackerError as e:
            messagebox.showerror("Błąd", str(e))
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowa wartość liczbowa.")

    def complete_task(self):
        selection = self.tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("Uwaga", "Wybierz najpierw zadanie z listy!")
            return
            
        idx = selection[0]
        self.manager.tasks[idx].is_done = True
        self.storage.save(self.manager)
        self.refresh_lists()

    def calc_calories(self):
        try:
            w = float(simpledialog.askstring("Kalkulator", "Podaj wagę (kg):"))
            h = float(simpledialog.askstring("Kalkulator", "Podaj wzrost (cm):"))
            a = int(simpledialog.askstring("Kalkulator", "Podaj wiek (lata):"))
            g = simpledialog.askstring("Kalkulator", "Płeć (m/k):")
            act = float(simpledialog.askstring("Kalkulator", "Mnożnik aktywności (np. 1.2 brak, 1.55 średnia):"))
            
            tdee = calculate_tdee(w, h, a, g, act)
            
            odp = messagebox.askyesno("Wynik", f"Twoje zapotrzebowanie to {tdee:.0f} kcal.\nCzy dodać to jako nawyk do śledzenia?")
            if odp:
                self.manager.add_habit(LimitHabit("Kalorie dzienne", round(tdee)))
                self.storage.save(self.manager)
                self.refresh_lists()
        except Exception as e:
            messagebox.showerror("Błąd", "Wprowadzono nieprawidłowe dane.")

if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerGUI(root)
    root.mainloop()