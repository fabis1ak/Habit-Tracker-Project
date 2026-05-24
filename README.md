# Habit & Task Tracker (Aplikacja do śledzenia nawyków i zadań)

Aplikacja desktopowa do zarządzania produktywnością zbudowana w Pythonie i Tkinterze. Pomaga budować nawyki, zarządzać zadaniami oraz śledzić codzienne postępy - a wszystkie dane są zapisywane lokalnie w pliku JSON.

---

## Funkcje

### Nawyki
- **Nawyki binarne** - śledzenie codziennych aktywności typu tak/nie (np. medytacja, trening).
- **Nawyki ilościowe** - śledzenie mierzalnych celów z dziennym limitem/celu (np. 2 l wody, 2500 kcal).
- **Licznik serii (streak)** - zobacz, ile dni z rzędu udało Ci się zrealizować swój cel.
- **Wskaźnik ukończenia z ostatnich 30 dni** - zwizualizowany za pomocą paska postępu w zakładce Statystyki.
- **Pasek postępu** - w przypadku nawyków ilościowych pozwala na szybkie porównanie dzisiejszego wyniku z założonym celem.
- **Pełny widok historii** - wgląd w każdy zalogowany wpis dla danego nawyku.
- **Usuwanie nawyków** - możliwość usunięcia nawyku wraz z całą jego historią.

### Zadania (To-Do)
- **Poziomy priorytetów** - Wysoki / Średni / Niski, oznaczone kolorami.
- **Terminy realizacji (due dates)** - opcjonalny termin dla każdego zadania (RRRR-MM-DD).
- **Wykrywanie zaległych zadań** - zadania po terminie są podświetlane na czerwono.
- **Filtry** - przeglądanie zadań: Wszystkie / W toku / Zakończone.
- **Oznacz jako wykonane** - ukończenie zadania jednym kliknięciem.
- **Usuwanie i masowe czyszczenie** - usuwanie pojedynczych zadań lub natychmiastowe czyszczenie wszystkich ukończonych.

### Statystyki
- Karty podsumowania: łączna liczba nawyków, ukończone zadania, najlepsza seria (streak), średni wskaźnik ukończenia.
- Szczegółowe zestawienie dla każdego nawyku: seria, wskaźnik ukończenia z ostatnich 30 dni wraz z paskiem postępu.
- Lista zaległych zadań.

### Narzędzia
- **Kalkulator TDEE** - wzór Mifflina-St Jeora z mnożnikiem aktywności; wynik można natychmiast dodać jako nowy nawyk.
- **Eksport do CSV** - eksport pełnej historii nawyków do pliku `habits_export.csv`.

---

## Stack technologiczny

| Warstwa | Technologia |
|---|---|
| Język | Python 3.10+ |
| GUI | Tkinter + ttk (wbudowane) |
| Przechowywanie danych | JSON (plik lokalny) |
| Architektura | OOP (Programowanie obiektowe) - modele, storage, utils, wyjątki |

Aplikacja nie wymaga żadnych zewnętrznych zależności (bibliotek).

---

## Struktura projektu

HabitTrackerProject/
├── main.py          # GUI - wszystkie okna, zakładki, okna dialogowe
├── models.py        # Modele: Habit, LimitHabit, BinaryHabit, Task, AppManager
├── storage.py       # Zapis/odczyt JSON (DataStorage)
├── utils.py         # Walidacja dat, kalkulator TDEE, generatory
├── exceptions.py    # Własna hierarchia wyjątków
└── data.json        # Tworzony automatycznie przy pierwszym zapisie