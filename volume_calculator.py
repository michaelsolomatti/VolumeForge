#!/usr/bin/env python3
"""
volume_calculator.py - Калькулятор объёма тел на Python (CLI + Tkinter GUI)
Поддерживает: 10 3D-фигур, историю, экспорт CSV, единицы измерения.
"""
import math
import json
import os
import csv
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Callable

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

HISTORY_FILE = "volume_history.json"
PI = math.pi

# ========== ФУНКЦИИ ОБЪЁМА ==========
def cube_volume(side: float) -> float:
    return side ** 3

def sphere_volume(radius: float) -> float:
    return 4/3 * PI * radius ** 3

def cylinder_volume(radius: float, height: float) -> float:
    return PI * radius ** 2 * height

def cone_volume(radius: float, height: float) -> float:
    return 1/3 * PI * radius ** 2 * height

def parallelepiped_volume(length: float, width: float, height: float) -> float:
    return length * width * height

def pyramid_volume(base_area: float, height: float) -> float:
    return 1/3 * base_area * height

def prism_volume(base_area: float, height: float) -> float:
    return base_area * height

def torus_volume(major_radius: float, minor_radius: float) -> float:
    return 2 * PI ** 2 * major_radius * minor_radius ** 2

def ellipsoid_volume(a: float, b: float, c: float) -> float:
    return 4/3 * PI * a * b * c

def frustum_volume(radius1: float, radius2: float, height: float) -> float:
    return 1/3 * PI * height * (radius1 ** 2 + radius1 * radius2 + radius2 ** 2)

# ========== СЛОВАРЬ ФИГУР ==========
def get_shapes() -> Dict[str, Tuple[str, Callable, List[str], str]]:
    return {
        '1': ('Куб', cube_volume, ['сторону'], 'a'),
        '2': ('Шар', sphere_volume, ['радиус'], 'r'),
        '3': ('Цилиндр', cylinder_volume, ['радиус', 'высоту'], 'r, h'),
        '4': ('Конус', cone_volume, ['радиус', 'высоту'], 'r, h'),
        '5': ('Параллелепипед', parallelepiped_volume, ['длину', 'ширину', 'высоту'], 'a, b, c'),
        '6': ('Пирамида', pyramid_volume, ['площадь основания', 'высоту'], 'S, h'),
        '7': ('Призма', prism_volume, ['площадь основания', 'высоту'], 'S, h'),
        '8': ('Тор', torus_volume, ['большой радиус', 'малый радиус'], 'R, r'),
        '9': ('Эллипсоид', ellipsoid_volume, ['полуось a', 'полуось b', 'полуось c'], 'a, b, c'),
        '10': ('Усечённый конус', frustum_volume, ['радиус 1', 'радиус 2', 'высоту'], 'r1, r2, h'),
    }

# ========== ИСТОРИЯ ==========
def save_history(entry: Dict) -> None:
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            pass
    history.append(entry)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def load_history() -> List[Dict]:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def export_csv(filename: str) -> None:
    history = load_history()
    if not history:
        print("История пуста.")
        return
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Дата', 'Фигура', 'Параметры', 'Объём', 'Единицы'])
        for entry in history:
            writer.writerow([entry['date'][:19], entry['shape'], entry['params'], entry['result'], entry.get('units', 'куб. ед.')])
    print(f"Экспортировано в {filename}")

# ========== CLI ==========
def interactive_cli():
    print("📦 КАЛЬКУЛЯТОР ОБЪЁМА ТЕЛ")
    shapes = get_shapes()
    history = load_history()
    units = "куб. ед."

    while True:
        print("\nВыберите фигуру:")
        for key, (name, _, _, _) in shapes.items():
            print(f"{key}. {name}")
        print("h. Показать историю")
        print("e. Экспорт CSV")
        print("u. Сменить единицы измерения")
        print("0. Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == '0':
            break
        elif choice.lower() == 'h':
            if not history:
                print("История пуста.")
            else:
                print("\n=== ИСТОРИЯ ===")
                for entry in history[-10:]:
                    print(f"{entry['date'][:19]} | {entry['shape']} | {entry['result']}")
            continue
        elif choice.lower() == 'e':
            filename = input("Имя CSV файла (по умолчанию volume_history.csv): ").strip()
            if not filename:
                filename = "volume_history.csv"
            export_csv(filename)
            continue
        elif choice.lower() == 'u':
            print("Доступные единицы: куб. ед., см³, м³, дм³, л, in³")
            units = input("Выберите единицы: ").strip()
            if not units:
                units = "куб. ед."
            continue
        elif choice in shapes:
            name, func, param_names, _ = shapes[choice]
            params = []
            print(f"\nФигура: {name}")
            for pname in param_names:
                while True:
                    try:
                        val = float(input(f"Введите {pname}: "))
                        if val <= 0:
                            print("Значение должно быть положительным.")
                            continue
                        params.append(val)
                        break
                    except ValueError:
                        print("Введите число.")
            result = func(*params)
            result_str = f"{result:.4f} {units}"
            print(f"\nОбъём {name.lower()}: {result_str}")

            save = input("Сохранить результат? (y/n): ").strip().lower()
            if save == 'y':
                entry = {
                    'date': datetime.now().isoformat(),
                    'shape': name,
                    'params': ', '.join(str(p) for p in params),
                    'result': result_str,
                    'units': units
                }
                save_history(entry)
                history.append(entry)
                print("✅ Сохранено!")
        else:
            print("Неверный выбор.")

# ========== GUI ==========
if GUI_AVAILABLE:
    class VolumeCalculatorGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("📦 Калькулятор объёма тел")
            self.root.geometry("750x600")
            self.root.resizable(True, True)
            self.shapes = get_shapes()
            self.history = load_history()
            self.units = "куб. ед."
            self.create_widgets()
            self.update_params()

        def create_widgets(self):
            main = ttk.Frame(self.root, padding="10")
            main.pack(fill=tk.BOTH, expand=True)

            # Верхняя панель
            top = ttk.Frame(main)
            top.pack(fill=tk.X, pady=5)
            ttk.Label(top, text="Фигура:").pack(side=tk.LEFT)
            self.shape_var = tk.StringVar()
            self.shape_combo = ttk.Combobox(top, textvariable=self.shape_var, values=[f"{k}. {v[0]}" for k, v in self.shapes.items()], state="readonly", width=25)
            self.shape_combo.pack(side=tk.LEFT, padx=5)
            self.shape_combo.bind("<<ComboboxSelected>>", lambda e: self.update_params())

            ttk.Label(top, text="Единицы:").pack(side=tk.LEFT, padx=(20,5))
            self.units_var = tk.StringVar(value="куб. ед.")
            units_combo = ttk.Combobox(top, textvariable=self.units_var, values=["куб. ед.", "см³", "м³", "дм³", "л", "in³"], state="readonly", width=8)
            units_combo.pack(side=tk.LEFT, padx=5)

            ttk.Button(top, text="📊 История", command=self.show_history).pack(side=tk.LEFT, padx=5)
            ttk.Button(top, text="💾 Экспорт CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)

            # Параметры
            self.params_frame = ttk.LabelFrame(main, text="Параметры")
            self.params_frame.pack(fill=tk.X, pady=5)
            self.param_entries = {}

            # Кнопка расчёта
            ttk.Button(main, text="🧮 Рассчитать", command=self.calculate).pack(pady=10)

            # Результат
            self.result_frame = ttk.LabelFrame(main, text="Результат")
            self.result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            self.result_text = scrolledtext.ScrolledText(self.result_frame, height=10)
            self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # История
            self.history_frame = ttk.LabelFrame(main, text="Последние вычисления")
            self.history_frame.pack(fill=tk.X, pady=5)
            self.history_listbox = tk.Listbox(self.history_frame, height=4)
            self.history_listbox.pack(fill=tk.X, padx=5, pady=5)
            self.refresh_history()

        def update_params(self):
            for widget in self.params_frame.winfo_children():
                widget.destroy()
            self.param_entries.clear()

            selection = self.shape_var.get()
            if not selection:
                return
            key = selection.split('.')[0]
            if key not in self.shapes:
                return
            _, _, param_names, _ = self.shapes[key]

            for i, pname in enumerate(param_names):
                ttk.Label(self.params_frame, text=f"{pname.capitalize()}:").grid(row=i, column=0, padx=5, pady=5, sticky="w")
                entry = ttk.Entry(self.params_frame, width=15)
                entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
                self.param_entries[pname] = entry

        def calculate(self):
            selection = self.shape_var.get()
            if not selection:
                messagebox.showwarning("Внимание", "Выберите фигуру")
                return
            key = selection.split('.')[0]
            if key not in self.shapes:
                return
            name, func, param_names, _ = self.shapes[key]

            params = []
            for pname in param_names:
                entry = self.param_entries.get(pname)
                if not entry:
                    return
                try:
                    val = float(entry.get().strip())
                    if val <= 0:
                        messagebox.showerror("Ошибка", f"'{pname}' должно быть положительным.")
                        return
                    params.append(val)
                except ValueError:
                    messagebox.showerror("Ошибка", f"Введите число для '{pname}'.")
                    return

            result = func(*params)
            units = self.units_var.get()
            result_str = f"{result:.4f} {units}"
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Фигура: {name}\n")
            self.result_text.insert(tk.END, f"Параметры: {', '.join(str(p) for p in params)}\n")
            self.result_text.insert(tk.END, f"Объём: {result_str}\n")

            # Сохраняем в историю
            entry = {
                'date': datetime.now().isoformat(),
                'shape': name,
                'params': ', '.join(str(p) for p in params),
                'result': result_str,
                'units': units
            }
            save_history(entry)
            self.history.append(entry)
            self.refresh_history()

        def refresh_history(self):
            self.history_listbox.delete(0, tk.END)
            for entry in self.history[-5:]:
                self.history_listbox.insert(tk.END, f"{entry['shape']}: {entry['result']}")

        def show_history(self):
            if not self.history:
                messagebox.showinfo("История", "История пуста.")
                return
            win = tk.Toplevel(self.root)
            win.title("История вычислений")
            win.geometry("600x400")
            text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
            text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text.insert(tk.END, f"{'Дата':<25} {'Фигура':<15} {'Результат':<20}\n")
            text.insert(tk.END, "-" * 60 + "\n")
            for entry in self.history[-20:]:
                text.insert(tk.END, f"{entry['date'][:19]:<25} {entry['shape']:<15} {entry['result']:<20}\n")
            text.config(state='disabled')

        def export_csv(self):
            filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
            if filename:
                export_csv(filename)
                messagebox.showinfo("Экспорт", f"Экспортировано в {filename}")

if __name__ == "__main__":
    if GUI_AVAILABLE:
        root = tk.Tk()
        app = VolumeCalculatorGUI(root)
        root.mainloop()
    else:
        interactive_cli()
