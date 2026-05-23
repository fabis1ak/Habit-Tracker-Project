import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
import csv
import os

from models import AppManager, LimitHabit, BinaryHabit, Task
from storage import DataStorage
from utils import validate_date, calculate_tdee
from exceptions import HabitTrackerError

# ── Paleta kolorów ──────────────────────────────────────────────────────
BG       = "#1e1e2e"
SURFACE  = "#2a2a3e"
SURFACE2 = "#313149"
ACCENT   = "#7c3aed"
ACC_LT   = "#9f5eff"
SUCCESS  = "#22c55e"
WARNING  = "#f59e0b"
DANGER   = "#ef4444"
TEXT     = "#e2e8f0"
SUBTEXT  = "#94a3b8"
WHITE    = "#ffffff"

DAYS_PL   = ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota", "Niedziela"]
MONTHS_PL = ["", "stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca",
             "lipca", "sierpnia", "września", "października", "listopada", "grudnia"]

PRIORITY_LABELS = {"high": "Wysoki", "medium": "Średni", "low": "Niski"}


def _date_pl(d: date) -> str:
    return f"{DAYS_PL[d.weekday()]}, {d.day} {MONTHS_PL[d.month]} {d.year}"


def apply_theme(root: tk.Tk) -> ttk.Style:
    root.configure(bg=BG)
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=BG, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=TEXT)

    style.configure("TNotebook", background=BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=SURFACE, foreground=SUBTEXT,
                    padding=[14, 8], font=("Segoe UI", 10))
    style.map("TNotebook.Tab",
              background=[("selected", ACCENT), ("active", SURFACE2)],
              foreground=[("selected", WHITE), ("active", TEXT)])

    style.configure("Treeview", background=SURFACE, foreground=TEXT,
                    fieldbackground=SURFACE, borderwidth=0, rowheight=28,
                    font=("Segoe UI", 10))
    style.configure("Treeview.Heading", background=SURFACE2, foreground=SUBTEXT,
                    font=("Segoe UI", 9, "bold"), borderwidth=0, relief="flat")
    style.map("Treeview",
              background=[("selected", ACCENT)],
              foreground=[("selected", WHITE)])

    style.configure("Horizontal.TProgressbar", background=SUCCESS,
                    troughcolor=SURFACE2, borderwidth=0, thickness=10)

    style.configure("Accent.TButton", background=ACCENT, foreground=WHITE,
                    font=("Segoe UI", 10), borderwidth=0, padding=[12, 6])
    style.map("Accent.TButton", background=[("active", ACC_LT)])

    style.configure("Danger.TButton", background=DANGER, foreground=WHITE,
                    font=("Segoe UI", 10), borderwidth=0, padding=[12, 6])
    style.map("Danger.TButton", background=[("active", "#f87171")])

    style.configure("Muted.TButton", background=SURFACE2, foreground=TEXT,
                    font=("Segoe UI", 10), borderwidth=0, padding=[12, 6])
    style.map("Muted.TButton", background=[("active", SURFACE)])

    style.configure("TScrollbar", background=SURFACE2, troughcolor=BG,
                    borderwidth=0, arrowsize=14, relief="flat")

    return style


def make_scrolled_tree(parent, columns, headings, widths, height=12):
    frame = ttk.Frame(parent)
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
    for col, heading, width in zip(columns, headings, widths):
        tree.heading(col, text=heading)
        tree.column(col, width=width, minwidth=40, anchor="center")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)
    return frame, tree


# ── Dialogi ────────────────────────────────────────────────────────────

class AddHabitDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.title("Dodaj nawyk")
        self.geometry("360x250")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self._build()
        self.wait_window()

    def _build(self):
        tk.Label(self, text="Nowy nawyk", font=("Segoe UI", 13, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(16, 6))

        form = tk.Frame(self, bg=BG)
        form.pack(fill=tk.X, padx=28)

        tk.Label(form, text="Nazwa:", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9), width=12, anchor="w").grid(row=0, column=0, sticky="w", pady=7)
        self.name_var = tk.StringVar()
        tk.Entry(form, textvariable=self.name_var, bg=SURFACE, fg=TEXT,
                 insertbackground=TEXT, relief=tk.FLAT, width=22,
                 font=("Segoe UI", 10)).grid(row=0, column=1, padx=8, pady=7)

        tk.Label(form, text="Typ:", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9), width=12, anchor="w").grid(row=1, column=0, sticky="w", pady=7)
        self.type_var = tk.StringVar(value="binary")
        tf = tk.Frame(form, bg=BG)
        tf.grid(row=1, column=1, sticky="w", padx=8)
        tk.Radiobutton(tf, text="Binarny (tak/nie)", variable=self.type_var, value="binary",
                       bg=BG, fg=TEXT, selectcolor=SURFACE2, activebackground=BG,
                       font=("Segoe UI", 9), command=self._toggle).pack(anchor="w")
        tk.Radiobutton(tf, text="Ilościowy (z celem liczbowym)", variable=self.type_var, value="limit",
                       bg=BG, fg=TEXT, selectcolor=SURFACE2, activebackground=BG,
                       font=("Segoe UI", 9), command=self._toggle).pack(anchor="w")

        self.limit_row = tk.Frame(form, bg=BG)
        self.limit_row.grid(row=2, column=0, columnspan=2, sticky="w", pady=4)
        tk.Label(self.limit_row, text="Cel dzienny:", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.limit_var = tk.StringVar()
        self.limit_entry = tk.Entry(self.limit_row, textvariable=self.limit_var, bg=SURFACE, fg=TEXT,
                                    insertbackground=TEXT, relief=tk.FLAT, width=10,
                                    font=("Segoe UI", 10), state=tk.DISABLED)
        self.limit_entry.pack(side=tk.LEFT, padx=8)

        bf = tk.Frame(self, bg=BG)
        bf.pack(pady=14)
        ttk.Button(bf, text="Dodaj", style="Accent.TButton", command=self._confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="Anuluj", style="Muted.TButton", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _toggle(self):
        if self.type_var.get() == "limit":
            self.limit_entry.configure(state=tk.NORMAL)
        else:
            self.limit_entry.configure(state=tk.DISABLED)
            self.limit_var.set("")

    def _confirm(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Uwaga", "Podaj nazwę nawyku!", parent=self)
            return
        if self.type_var.get() == "limit":
            try:
                limit = float(self.limit_var.get())
                if limit <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Błąd", "Podaj prawidłową wartość większą od zera!", parent=self)
                return
            self.result = ("limit", name, limit)
        else:
            self.result = ("binary", name, None)
        self.destroy()


class AddTaskDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.result = None
        self.title("Nowe zadanie")
        self.geometry("360x230")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self._build()
        self.wait_window()

    def _build(self):
        tk.Label(self, text="Nowe zadanie", font=("Segoe UI", 13, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(16, 6))

        form = tk.Frame(self, bg=BG)
        form.pack(fill=tk.X, padx=28)

        tk.Label(form, text="Opis:", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9), width=12, anchor="w").grid(row=0, column=0, sticky="w", pady=7)
        self.desc_var = tk.StringVar()
        tk.Entry(form, textvariable=self.desc_var, bg=SURFACE, fg=TEXT,
                 insertbackground=TEXT, relief=tk.FLAT, width=22,
                 font=("Segoe UI", 10)).grid(row=0, column=1, padx=8, pady=7)

        tk.Label(form, text="Priorytet:", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9), width=12, anchor="w").grid(row=1, column=0, sticky="w", pady=7)
        self.priority_var = tk.StringVar(value="medium")
        pf = tk.Frame(form, bg=BG)
        pf.grid(row=1, column=1, sticky="w", padx=8)
        for val, label, color in [("high", "Wysoki", DANGER), ("medium", "Średni", WARNING), ("low", "Niski", SUCCESS)]:
            tk.Radiobutton(pf, text=label, variable=self.priority_var, value=val,
                           bg=BG, fg=color, selectcolor=SURFACE2, activebackground=BG,
                           font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=4)

        tk.Label(form, text="Termin:", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9), width=12, anchor="w").grid(row=2, column=0, sticky="w", pady=7)
        due_f = tk.Frame(form, bg=BG)
        due_f.grid(row=2, column=1, sticky="w", padx=8)
        self.due_var = tk.StringVar()
        tk.Entry(due_f, textvariable=self.due_var, bg=SURFACE, fg=TEXT,
                 insertbackground=TEXT, relief=tk.FLAT, width=13,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)
        tk.Label(due_f, text=" (opcjonalnie)", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 8)).pack(side=tk.LEFT)

        bf = tk.Frame(self, bg=BG)
        bf.pack(pady=12)
        ttk.Button(bf, text="Dodaj", style="Accent.TButton", command=self._confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="Anuluj", style="Muted.TButton", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _confirm(self):
        desc = self.desc_var.get().strip()
        if not desc:
            messagebox.showwarning("Uwaga", "Podaj opis zadania!", parent=self)
            return
        due = self.due_var.get().strip() or None
        if due:
            try:
                validate_date(due)
            except Exception:
                messagebox.showerror("Błąd", "Nieprawidłowy format daty!\nUżyj: RRRR-MM-DD", parent=self)
                return
        self.result = (desc, self.priority_var.get(), due)
        self.destroy()


class LogProgressDialog(tk.Toplevel):
    def __init__(self, parent, habit):
        super().__init__(parent)
        self.habit = habit
        self.result = None
        self.title("Zaloguj postęp")
        self.geometry("320x210")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self._build()
        self.wait_window()

    def _build(self):
        tk.Label(self, text=f"Postęp: {self.habit.name}", font=("Segoe UI", 12, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(16, 4))

        form = tk.Frame(self, bg=BG)
        form.pack(fill=tk.X, padx=28)

        tk.Label(form, text="Data:", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9), width=14, anchor="w").grid(row=0, column=0, sticky="w", pady=9)
        self.date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        tk.Entry(form, textvariable=self.date_var, bg=SURFACE, fg=TEXT,
                 insertbackground=TEXT, relief=tk.FLAT, width=14,
                 font=("Segoe UI", 10)).grid(row=0, column=1, padx=8)

        if isinstance(self.habit, LimitHabit):
            tk.Label(form, text=f"Wartość (cel: {self.habit.limit}):", bg=BG, fg=SUBTEXT,
                     font=("Segoe UI", 9), width=14, anchor="w").grid(row=1, column=0, sticky="w", pady=9)
            self.val_var = tk.StringVar()
            tk.Entry(form, textvariable=self.val_var, bg=SURFACE, fg=TEXT,
                     insertbackground=TEXT, relief=tk.FLAT, width=14,
                     font=("Segoe UI", 10)).grid(row=1, column=1, padx=8)
        else:
            self.val_var = tk.BooleanVar(value=True)
            tk.Label(form, text="Wykonano:", bg=BG, fg=SUBTEXT,
                     font=("Segoe UI", 9), width=14, anchor="w").grid(row=1, column=0, sticky="w", pady=9)
            tk.Checkbutton(form, variable=self.val_var, bg=BG, activebackground=BG,
                           selectcolor=SURFACE2, fg=TEXT).grid(row=1, column=1, sticky="w", padx=8)

        bf = tk.Frame(self, bg=BG)
        bf.pack(pady=14)
        ttk.Button(bf, text="Zapisz", style="Accent.TButton", command=self._confirm).pack(side=tk.LEFT, padx=5)
        ttk.Button(bf, text="Anuluj", style="Muted.TButton", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _confirm(self):
        try:
            validate_date(self.date_var.get())
        except Exception:
            messagebox.showerror("Błąd", "Nieprawidłowy format daty!\nUżyj: RRRR-MM-DD", parent=self)
            return
        if isinstance(self.habit, LimitHabit):
            try:
                val = float(self.val_var.get())
            except ValueError:
                messagebox.showerror("Błąd", "Podaj prawidłową wartość liczbową!", parent=self)
                return
            self.result = (self.date_var.get(), val)
        else:
            self.result = (self.date_var.get(), bool(self.val_var.get()))
        self.destroy()


# ── Główna aplikacja ───────────────────────────────────────────────────

class HabitTrackerGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Habit & Task Tracker")
        self.root.geometry("820x620")
        self.root.minsize(720, 520)

        self.manager = AppManager()
        self.storage = DataStorage()
        self.storage.load(self.manager)

        apply_theme(root)
        self._build_ui()
        self.refresh_all()

    # ── Budowanie UI ──────────────────────────────────────────────────

    def _build_ui(self):
        header = tk.Frame(self.root, bg=SURFACE, height=52)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="  Habit & Task Tracker", font=("Segoe UI", 14, "bold"),
                 bg=SURFACE, fg=TEXT).pack(side=tk.LEFT, padx=12, pady=14)
        tk.Label(header, text=_date_pl(date.today()), font=("Segoe UI", 9),
                 bg=SURFACE, fg=SUBTEXT).pack(side=tk.RIGHT, padx=16, pady=18)

        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=10, pady=(8, 4))

        self._build_habits_tab()
        self._build_tasks_tab()
        self._build_stats_tab()
        self._build_tools_tab()

        self.status_var = tk.StringVar(value="Gotowy.")
        tk.Label(self.root, textvariable=self.status_var, bg=SURFACE2, fg=SUBTEXT,
                 font=("Segoe UI", 8), anchor="w", padx=10, pady=3).pack(fill=tk.X, side=tk.BOTTOM)

    def _build_habits_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="  Nawyki  ")

        cols = ("name", "type", "today", "streak", "rate")
        headings = ("Nawyk", "Typ", "Dzisiaj", "Seria", "Ost. 30 dni")
        widths = (210, 95, 130, 80, 95)
        tf, self.habits_tree = make_scrolled_tree(frame, cols, headings, widths, height=13)
        self.habits_tree.column("name", anchor="w")
        tf.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))

        prog_frame = tk.Frame(frame, bg=BG)
        prog_frame.pack(fill=tk.X, padx=8, pady=(0, 4))
        self.habit_prog_label = tk.Label(prog_frame, text="", bg=BG, fg=SUBTEXT,
                                         font=("Segoe UI", 9))
        self.habit_prog_label.pack(side=tk.LEFT)
        self.habit_prog_bar = ttk.Progressbar(prog_frame, mode="determinate",
                                               style="Horizontal.TProgressbar", length=280)
        self.habit_prog_bar.pack(side=tk.LEFT, padx=8)

        self.habits_tree.bind("<<TreeviewSelect>>", self._on_habit_select)

        bf = tk.Frame(frame, bg=BG)
        bf.pack(fill=tk.X, padx=8, pady=(0, 8))
        ttk.Button(bf, text="+ Dodaj nawyk", style="Accent.TButton",
                   command=self.add_habit).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Zaloguj postęp", style="Muted.TButton",
                   command=self.log_progress).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Historia", style="Muted.TButton",
                   command=self.show_history).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Usuń nawyk", style="Danger.TButton",
                   command=self.delete_habit).pack(side=tk.RIGHT, padx=4)

    def _build_tasks_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="  Zadania  ")

        filter_frame = tk.Frame(frame, bg=BG)
        filter_frame.pack(fill=tk.X, padx=8, pady=(8, 2))
        tk.Label(filter_frame, text="Filtruj:", bg=BG, fg=SUBTEXT,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.task_filter = tk.StringVar(value="all")
        for val, label in [("all", "Wszystkie"), ("pending", "Do zrobienia"), ("done", "Ukończone")]:
            tk.Radiobutton(filter_frame, text=label, variable=self.task_filter, value=val,
                           bg=BG, fg=TEXT, selectcolor=SURFACE2, activebackground=BG,
                           font=("Segoe UI", 9), command=self.refresh_tasks).pack(side=tk.LEFT, padx=8)

        cols = ("priority", "desc", "due", "status")
        headings = ("Priorytet", "Opis", "Termin", "Status")
        widths = (90, 350, 110, 95)
        tf, self.tasks_tree = make_scrolled_tree(frame, cols, headings, widths, height=13)
        self.tasks_tree.column("desc", anchor="w")
        self.tasks_tree.tag_configure("done", foreground=SUBTEXT)
        self.tasks_tree.tag_configure("overdue", foreground=DANGER)
        tf.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        bf = tk.Frame(frame, bg=BG)
        bf.pack(fill=tk.X, padx=8, pady=(0, 8))
        ttk.Button(bf, text="+ Dodaj zadanie", style="Accent.TButton",
                   command=self.add_task).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Oznacz: zrobione", style="Muted.TButton",
                   command=self.complete_task).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Wyczyść ukończone", style="Muted.TButton",
                   command=self.clear_done_tasks).pack(side=tk.LEFT, padx=4)
        ttk.Button(bf, text="Usuń zadanie", style="Danger.TButton",
                   command=self.delete_task).pack(side=tk.RIGHT, padx=4)

    def _build_stats_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="  Statystyki  ")
        self._stats_outer = frame
        self._stats_inner = None

    def _build_tools_tab(self):
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text="  Narzędzia  ")

        tk.Label(frame, text="Kalkulator TDEE", font=("Segoe UI", 12, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(20, 2), padx=20, anchor="w")
        tk.Label(frame, text="Oblicz dzienne zapotrzebowanie kaloryczne metodą Mifflina-St Jeor.",
                 bg=BG, fg=SUBTEXT, font=("Segoe UI", 9)).pack(padx=20, anchor="w")

        form = tk.Frame(frame, bg=BG)
        form.pack(fill=tk.X, padx=20, pady=10)

        fields = [
            ("Waga (kg):", None),
            ("Wzrost (cm):", None),
            ("Wiek (lata):", None),
            ("Płeć (m/k):", None),
            ("Aktywność:", "1.2 brak / 1.375 lekka / 1.55 średnia / 1.725 ciężka"),
        ]
        self.tdee_vars = [tk.StringVar() for _ in fields]
        for i, ((label, hint), var) in enumerate(zip(fields, self.tdee_vars)):
            tk.Label(form, text=label, bg=BG, fg=SUBTEXT, font=("Segoe UI", 9),
                     width=14, anchor="w").grid(row=i, column=0, sticky="w", pady=5)
            tk.Entry(form, textvariable=var, bg=SURFACE, fg=TEXT, insertbackground=TEXT,
                     relief=tk.FLAT, width=18, font=("Segoe UI", 10)).grid(row=i, column=1, padx=8, pady=5, sticky="w")
            if hint:
                tk.Label(form, text=hint, bg=BG, fg=SUBTEXT,
                         font=("Segoe UI", 8)).grid(row=i, column=2, sticky="w", padx=4)

        self.tdee_result_var = tk.StringVar(value="")
        tk.Label(frame, textvariable=self.tdee_result_var, bg=BG, fg=SUCCESS,
                 font=("Segoe UI", 13, "bold")).pack(pady=4)

        bf = tk.Frame(frame, bg=BG)
        bf.pack(pady=4)
        ttk.Button(bf, text="Oblicz TDEE", style="Accent.TButton",
                   command=self.calc_tdee).pack(side=tk.LEFT, padx=6)
        ttk.Button(bf, text="Dodaj jako nawyk", style="Muted.TButton",
                   command=self.add_tdee_habit).pack(side=tk.LEFT, padx=6)

        tk.Frame(frame, bg=SURFACE2, height=1).pack(fill=tk.X, padx=20, pady=12)

        tk.Label(frame, text="Eksport danych", font=("Segoe UI", 12, "bold"),
                 bg=BG, fg=TEXT).pack(padx=20, anchor="w", pady=(0, 4))
        ttk.Button(frame, text="Eksportuj nawyki do CSV", style="Muted.TButton",
                   command=self.export_csv).pack(padx=20, pady=4, anchor="w")

        self._last_tdee = None

    # ── Odświeżanie danych ────────────────────────────────────────────

    def refresh_all(self):
        self.refresh_habits()
        self.refresh_tasks()
        self.refresh_stats()

    def refresh_habits(self):
        self.habits_tree.delete(*self.habits_tree.get_children())
        today = date.today().strftime("%Y-%m-%d")
        for habit in self.manager.habits:
            streak = habit.streak()
            rate = f"{habit.completion_rate():.0f}%"
            if isinstance(habit, LimitHabit):
                val = habit.history.get(today)
                today_str = f"{val} / {habit.limit}" if val is not None else "—"
            else:
                val = habit.history.get(today)
                today_str = "Tak" if val is True else ("Nie" if val is False else "—")
            typ = "Ilościowy" if isinstance(habit, LimitHabit) else "Binarny"
            self.habits_tree.insert("", tk.END, values=(habit.name, typ, today_str, f"{streak} dni", rate))
        self.habit_prog_label.config(text="")
        self.habit_prog_bar["value"] = 0

    def refresh_tasks(self):
        self.tasks_tree.delete(*self.tasks_tree.get_children())
        f = self.task_filter.get()
        today = date.today().strftime("%Y-%m-%d")
        for task in self.manager.tasks:
            if f == "pending" and task.is_done:
                continue
            if f == "done" and not task.is_done:
                continue
            p_label = PRIORITY_LABELS.get(task.priority, task.priority)
            due = task.due_date or "—"
            is_overdue = task.due_date and task.due_date < today and not task.is_done
            if task.is_done:
                status = "Zrobione"
                tag = "done"
            elif is_overdue:
                status = "Po terminie!"
                tag = "overdue"
            else:
                status = "Oczekuje"
                tag = ""
            self.tasks_tree.insert("", tk.END, values=(p_label, task.description, due, status), tags=(tag,))

    def refresh_stats(self):
        if self._stats_inner:
            self._stats_inner.destroy()

        canvas = tk.Canvas(self._stats_outer, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(self._stats_outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = tk.Frame(canvas, bg=BG)
        self._stats_inner = inner
        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(window_id, width=canvas.winfo_width())

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width))

        # Karty podsumowania
        total_habits = len(self.manager.habits)
        done_tasks = sum(1 for t in self.manager.tasks if t.is_done)
        total_tasks = len(self.manager.tasks)
        best_streak = max((h.streak() for h in self.manager.habits), default=0)
        avg_rate = (sum(h.completion_rate() for h in self.manager.habits) / total_habits
                    if total_habits else 0)

        cards_frame = tk.Frame(inner, bg=BG)
        cards_frame.pack(fill=tk.X, padx=16, pady=(16, 8))

        for title, value, color in [
            ("Nawyki", str(total_habits), ACCENT),
            ("Zadania ukończone", f"{done_tasks}/{total_tasks}", SUCCESS),
            ("Najlepsza seria", f"{best_streak} dni", WARNING),
            ("Śr. realizacja", f"{avg_rate:.0f}%", ACC_LT),
        ]:
            card = tk.Frame(cards_frame, bg=SURFACE, padx=18, pady=12)
            card.pack(side=tk.LEFT, padx=6, ipadx=6)
            tk.Label(card, text=title, bg=SURFACE, fg=SUBTEXT,
                     font=("Segoe UI", 9)).pack()
            tk.Label(card, text=value, bg=SURFACE, fg=color,
                     font=("Segoe UI", 20, "bold")).pack()

        if not self.manager.habits:
            tk.Label(inner, text="Brak nawyków. Dodaj pierwszy nawyk w zakładce Nawyki.",
                     bg=BG, fg=SUBTEXT, font=("Segoe UI", 10)).pack(pady=30)
            return

        tk.Label(inner, text="Szczegóły nawyków — ostatnie 30 dni",
                 font=("Segoe UI", 11, "bold"), bg=BG, fg=TEXT).pack(anchor="w", padx=16, pady=(12, 4))

        for habit in self.manager.habits:
            hf = tk.Frame(inner, bg=SURFACE, padx=14, pady=10)
            hf.pack(fill=tk.X, padx=16, pady=3)

            typ = "Ilościowy" if isinstance(habit, LimitHabit) else "Binarny"
            tk.Label(hf, text=f"{habit.name}  ({typ})", bg=SURFACE, fg=TEXT,
                     font=("Segoe UI", 10, "bold"), width=28, anchor="w").pack(side=tk.LEFT)

            streak = habit.streak()
            rate = habit.completion_rate()
            rate_color = SUCCESS if rate >= 70 else (WARNING if rate >= 40 else DANGER)

            tk.Label(hf, text=f"Seria: {streak} dni", bg=SURFACE, fg=WARNING,
                     font=("Segoe UI", 9), width=14).pack(side=tk.LEFT)
            tk.Label(hf, text=f"Realizacja: {rate:.0f}%", bg=SURFACE, fg=rate_color,
                     font=("Segoe UI", 9), width=16).pack(side=tk.LEFT)

            bar = ttk.Progressbar(hf, mode="determinate", length=140,
                                  style="Horizontal.TProgressbar")
            bar["value"] = rate
            bar.pack(side=tk.LEFT, padx=8)

        # Zadania po terminie
        today = date.today().strftime("%Y-%m-%d")
        overdue = [t for t in self.manager.tasks if t.due_date and t.due_date < today and not t.is_done]
        if overdue:
            tk.Label(inner, text="Zadania po terminie", font=("Segoe UI", 11, "bold"),
                     bg=BG, fg=DANGER).pack(anchor="w", padx=16, pady=(14, 4))
            for task in overdue:
                tf = tk.Frame(inner, bg=SURFACE, padx=14, pady=8)
                tf.pack(fill=tk.X, padx=16, pady=2)
                tk.Label(tf, text=task.description, bg=SURFACE, fg=DANGER,
                         font=("Segoe UI", 10), anchor="w").pack(side=tk.LEFT)
                tk.Label(tf, text=f"  Termin: {task.due_date}", bg=SURFACE, fg=SUBTEXT,
                         font=("Segoe UI", 9)).pack(side=tk.LEFT)

    # ── Obsługa nawyków ───────────────────────────────────────────────

    def _on_habit_select(self, _=None):
        sel = self.habits_tree.selection()
        if not sel:
            return
        idx = self.habits_tree.index(sel[0])
        if idx >= len(self.manager.habits):
            return
        habit = self.manager.habits[idx]
        if isinstance(habit, LimitHabit):
            today = date.today().strftime("%Y-%m-%d")
            val = habit.history.get(today) or 0
            pct = min(val / habit.limit * 100, 100) if habit.limit else 0
            self.habit_prog_bar["value"] = pct
            self.habit_prog_label.config(text=f"{habit.name}: {val} / {habit.limit}  ")
        else:
            self.habit_prog_bar["value"] = 0
            self.habit_prog_label.config(text="")

    def add_habit(self):
        dlg = AddHabitDialog(self.root)
        if not dlg.result:
            return
        typ, name, limit = dlg.result
        try:
            self.manager.add_habit(LimitHabit(name, limit) if typ == "limit" else BinaryHabit(name))
            self.manager.sort_habits()
            self.storage.save(self.manager)
            self.refresh_all()
            self.status_var.set(f"Dodano nawyk: {name}")
        except HabitTrackerError as e:
            messagebox.showerror("Błąd", str(e))

    def log_progress(self):
        sel = self.habits_tree.selection()
        if not sel:
            messagebox.showwarning("Uwaga", "Wybierz nawyk z listy!")
            return
        idx = self.habits_tree.index(sel[0])
        habit = self.manager.habits[idx]
        dlg = LogProgressDialog(self.root, habit)
        if not dlg.result:
            return
        date_str, value = dlg.result
        try:
            habit.log_progress(date_str, value)
            self.storage.save(self.manager)
            self.refresh_all()
            self.status_var.set(f"Zapisano postęp dla: {habit.name}")
        except HabitTrackerError as e:
            messagebox.showerror("Błąd", str(e))

    def delete_habit(self):
        sel = self.habits_tree.selection()
        if not sel:
            messagebox.showwarning("Uwaga", "Wybierz nawyk do usunięcia!")
            return
        idx = self.habits_tree.index(sel[0])
        habit = self.manager.habits[idx]
        if messagebox.askyesno("Potwierdzenie",
                               f"Usunąć nawyk '{habit.name}'?\nCała historia zostanie utracona."):
            self.manager.delete_habit(idx)
            self.storage.save(self.manager)
            self.refresh_all()
            self.status_var.set(f"Usunięto nawyk: {habit.name}")

    def show_history(self):
        sel = self.habits_tree.selection()
        if not sel:
            messagebox.showwarning("Uwaga", "Wybierz nawyk!")
            return
        idx = self.habits_tree.index(sel[0])
        habit = self.manager.habits[idx]

        win = tk.Toplevel(self.root)
        win.title(f"Historia: {habit.name}")
        win.geometry("320x430")
        win.configure(bg=BG)

        tk.Label(win, text=f"Historia: {habit.name}", font=("Segoe UI", 12, "bold"),
                 bg=BG, fg=TEXT).pack(pady=(14, 4))

        if not habit.history:
            tk.Label(win, text="Brak zapisanych wpisów.", bg=BG, fg=SUBTEXT).pack(pady=20)
            return

        tf, tree = make_scrolled_tree(win, ("date", "value"), ("Data", "Wartość"), (150, 130), height=15)
        tf.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        for d, v in sorted(habit.history.items(), reverse=True):
            display = "Tak" if v is True else ("Nie" if v is False else str(v))
            tree.insert("", tk.END, values=(d, display))

    # ── Obsługa zadań ─────────────────────────────────────────────────

    def _visible_task_indices(self):
        f = self.task_filter.get()
        return [i for i, t in enumerate(self.manager.tasks)
                if not (f == "pending" and t.is_done) and not (f == "done" and not t.is_done)]

    def add_task(self):
        dlg = AddTaskDialog(self.root)
        if not dlg.result:
            return
        desc, priority, due = dlg.result
        self.manager.add_task(Task(desc, priority=priority, due_date=due))
        self.storage.save(self.manager)
        self.refresh_tasks()
        self.refresh_stats()
        self.status_var.set(f"Dodano zadanie: {desc}")

    def complete_task(self):
        sel = self.tasks_tree.selection()
        if not sel:
            messagebox.showwarning("Uwaga", "Wybierz zadanie!")
            return
        visible = self._visible_task_indices()
        actual = visible[self.tasks_tree.index(sel[0])]
        self.manager.tasks[actual].is_done = True
        self.storage.save(self.manager)
        self.refresh_tasks()
        self.refresh_stats()
        self.status_var.set("Zadanie oznaczone jako ukończone.")

    def delete_task(self):
        sel = self.tasks_tree.selection()
        if not sel:
            messagebox.showwarning("Uwaga", "Wybierz zadanie!")
            return
        visible = self._visible_task_indices()
        actual = visible[self.tasks_tree.index(sel[0])]
        task = self.manager.tasks[actual]
        if messagebox.askyesno("Potwierdzenie", f"Usunąć zadanie:\n'{task.description}'?"):
            self.manager.delete_task(actual)
            self.storage.save(self.manager)
            self.refresh_tasks()
            self.refresh_stats()
            self.status_var.set(f"Usunięto zadanie: {task.description}")

    def clear_done_tasks(self):
        done = [t for t in self.manager.tasks if t.is_done]
        if not done:
            messagebox.showinfo("Info", "Brak ukończonych zadań.")
            return
        if messagebox.askyesno("Potwierdzenie", f"Usunąć {len(done)} ukończonych zadań?"):
            self.manager.tasks = [t for t in self.manager.tasks if not t.is_done]
            self.storage.save(self.manager)
            self.refresh_tasks()
            self.refresh_stats()
            self.status_var.set(f"Usunięto {len(done)} ukończonych zadań.")

    # ── Narzędzia ─────────────────────────────────────────────────────

    def calc_tdee(self):
        try:
            w   = float(self.tdee_vars[0].get())
            h   = float(self.tdee_vars[1].get())
            a   = int(self.tdee_vars[2].get())
            g   = self.tdee_vars[3].get().strip()
            act = float(self.tdee_vars[4].get())
            self._last_tdee = calculate_tdee(w, h, a, g, act)
            self.tdee_result_var.set(f"Twoje TDEE: {self._last_tdee:.0f} kcal / dzień")
            self.status_var.set(f"TDEE: {self._last_tdee:.0f} kcal")
        except HabitTrackerError as e:
            messagebox.showerror("Błąd", str(e))
        except Exception:
            messagebox.showerror("Błąd", "Sprawdź poprawność wprowadzonych danych.")

    def add_tdee_habit(self):
        if not self._last_tdee:
            messagebox.showwarning("Uwaga", "Najpierw oblicz TDEE!")
            return
        self.manager.add_habit(LimitHabit("Kalorie dzienne", round(self._last_tdee)))
        self.manager.sort_habits()
        self.storage.save(self.manager)
        self.refresh_all()
        self.nb.select(0)
        self.status_var.set("Dodano nawyk: Kalorie dzienne")

    def export_csv(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "habits_export.csv")
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Nawyk", "Typ", "Cel", "Data", "Wartość", "Ukończone"])
            for habit in self.manager.habits:
                typ = "Ilościowy" if isinstance(habit, LimitHabit) else "Binarny"
                cel = habit.limit if isinstance(habit, LimitHabit) else "—"
                for d, v in sorted(habit.history.items()):
                    ukonczone = "Tak" if habit._is_completed(d) else "Nie"
                    writer.writerow([habit.name, typ, cel, d, v, ukonczone])
        messagebox.showinfo("Eksport zakończony", f"Plik zapisany:\n{path}")
        self.status_var.set(f"Wyeksportowano do: {path}")


if __name__ == "__main__":
    root = tk.Tk()
    app = HabitTrackerGUI(root)
    root.mainloop()
