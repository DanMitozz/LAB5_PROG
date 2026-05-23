#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI приложение для лабораторной работы 5.1
Внешняя сортировка больших файлов - База данных сотрудников
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys
import threading
from datetime import datetime
import shutil


class SortApp:
    """Главное приложение"""

    def __init__(self, root):
        self.root = root
        self.root.title("Внешняя сортировка - Лабораторная работа 5.1")
        self.root.geometry("1000x800")

        # Переменные состояния
        self.data_file = tk.StringVar(value="data.csv")
        self.sort_key = tk.IntVar(value=0)
        self.language = tk.StringVar(value="python")
        self.sorting_in_progress = False
        self.cpp_compiler_path = None

        self.find_cpp_compiler()
        self.setup_ui()
        self.setup_context_menu()

    def find_cpp_compiler(self):
        """Поиск компилятора C++ в системе"""
        possible_paths = [
            r"C:\msys64\mingw64\bin\g++.exe",
            r"C:\msys64\ucrt64\bin\g++.exe",
            "g++", "g++.exe"
        ]
        for path in possible_paths:
            if os.path.exists(path) or shutil.which(path):
                self.cpp_compiler_path = path
                return True
        return False

    def setup_ui(self):
        """Настройка интерфейса"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Заголовок
        title = ttk.Label(main_frame, text="Внешняя сортировка больших файлов\n"
                                           "База данных сотрудников компании",
                          font=('Arial', 16, 'bold'), justify='center')
        title.grid(row=0, column=0, columnspan=4, pady=10)

        self.setup_generation_frame(main_frame)
        self.setup_file_frame(main_frame)
        self.setup_sort_frame(main_frame)
        self.setup_control_frame(main_frame)
        self.setup_filter_frame(main_frame)
        self.setup_output_frame(main_frame)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)

    def setup_generation_frame(self, parent):
        """Фрейм генерации данных"""
        frame = ttk.LabelFrame(parent, text="Генерация данных", padding="10")
        frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(frame, text="Размер (ГБ):").grid(row=0, column=0, sticky=tk.W)
        self.size_var = tk.StringVar(value="1.1")
        size_spinbox = ttk.Spinbox(frame, from_=0.1, to=2.0, increment=0.1,
                                   textvariable=self.size_var, width=10)
        size_spinbox.grid(row=0, column=1, padx=5)

        ttk.Button(frame, text="Сгенерировать (полный файл)",
                   command=self.generate_full_data).grid(row=0, column=2, padx=5)
        ttk.Button(frame, text="Сгенерировать (тестовый)",
                   command=self.generate_test_data).grid(row=0, column=3, padx=5)

        self.gen_status = ttk.Label(frame, text="", foreground="blue")
        self.gen_status.grid(row=0, column=4, padx=10)

    def setup_file_frame(self, parent):
        """Фрейм выбора файла"""
        frame = ttk.LabelFrame(parent, text="Выбор файла", padding="10")
        frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(frame, text="Файл данных:").grid(row=0, column=0, sticky=tk.W)
        file_entry = ttk.Entry(frame, textvariable=self.data_file, width=60)
        file_entry.grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Обзор", command=self.select_file).grid(row=0, column=2, padx=5)

        self.file_info_label = ttk.Label(frame, text="", foreground="gray")
        self.file_info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=5)
        self.update_file_info()

    def setup_sort_frame(self, parent):
        """Фрейм настроек сортировки"""
        frame = ttk.LabelFrame(parent, text="Настройки сортировки", padding="10")
        frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(frame, text="Язык реализации:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(frame, text="Python", variable=self.language,
                        value="python").grid(row=0, column=1, sticky=tk.W)

        if self.cpp_compiler_path:
            ttk.Radiobutton(frame, text="C++", variable=self.language,
                            value="cpp").grid(row=0, column=2, sticky=tk.W)
        else:
            ttk.Radiobutton(frame, text="C++ (недоступен)", variable=self.language,
                            value="cpp", state="disabled").grid(row=0, column=2, sticky=tk.W)

        ttk.Label(frame, text="Ключ сортировки:").grid(row=1, column=0, sticky=tk.W, pady=5)
        sort_keys = [("ID", 0), ("ФИО", 1), ("Отдел", 2),
                     ("Должность", 3), ("Зарплата", 4), ("Статус", 5), ("Дата увольнения", 6)]

        for i, (text, value) in enumerate(sort_keys):
            ttk.Radiobutton(frame, text=text, variable=self.sort_key,
                            value=value).grid(row=1, column=i + 1, sticky=tk.W, padx=5)

    def setup_control_frame(self, parent):
        """Фрейм управления - кнопки действий"""
        frame = ttk.Frame(parent)
        frame.grid(row=4, column=0, columnspan=4, pady=10)

        self.sort_btn = ttk.Button(frame, text="Начать сортировку",
                                   command=self.start_sort, width=20)
        self.sort_btn.grid(row=0, column=0, padx=5)

        ttk.Button(frame, text="Проверить результат",
                   command=self.verify_sort, width=20).grid(row=0, column=1, padx=5)

        ttk.Button(frame, text="Просмотреть файл",
                   command=self.view_file, width=20).grid(row=0, column=2, padx=5)

        ttk.Button(frame, text="Статистика",
                   command=self.show_statistics, width=20).grid(row=0, column=3, padx=5)

        ttk.Button(frame, text="Очистить вывод",
                   command=self.clear_output, width=20).grid(row=0, column=4, padx=5)

    def setup_filter_frame(self, parent):
        """Фрейм фильтрации по статусу"""
        frame = ttk.LabelFrame(parent, text="Фильтрация по статусу", padding="10")
        frame.grid(row=5, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)

        ttk.Button(frame, text="Все сотрудники",
                   command=self.show_all_employees).grid(row=0, column=0, padx=5)
        ttk.Button(frame, text="Только активные",
                   command=self.show_active_employees).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Только уволенные",
                   command=self.show_fired_employees).grid(row=0, column=2, padx=5)

    def setup_output_frame(self, parent):
        """Фрейм вывода информации"""
        frame = ttk.LabelFrame(parent, text="Вывод", padding="10")
        frame.grid(row=6, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        text_frame = ttk.Frame(frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.output_text = tk.Text(text_frame, height=20, width=90,
                                   font=('Consolas', 10),
                                   yscrollcommand=scrollbar.set,
                                   wrap=tk.WORD)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.output_text.yview)

        # Цвета для разных типов сообщений
        self.output_text.tag_config("timestamp", foreground="gray")
        self.output_text.tag_config("info", foreground="black")
        self.output_text.tag_config("error", foreground="red")
        self.output_text.tag_config("success", foreground="green")
        self.output_text.tag_config("warning", foreground="orange")

    def setup_context_menu(self):
        """Контекстное меню для копирования текста"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_selected)
        self.context_menu.add_command(label="Копировать всё", command=self.copy_all)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Очистить", command=self.clear_output)

        self.output_text.bind("<Button-3>", self.show_context_menu)
        self.output_text.bind("<Control-c>", lambda e: self.copy_selected())
        self.output_text.bind("<Control-a>", lambda e: self.select_all())

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def copy_selected(self):
        try:
            selected = self.output_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        except tk.TclError:
            pass

    def copy_all(self):
        all_text = self.output_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(all_text)

    def select_all(self):
        self.output_text.tag_add(tk.SEL, 1.0, tk.END)
        self.output_text.mark_set(tk.INSERT, 1.0)

    def log(self, message: str, tag: str = "info"):
        """Вывод сообщения с временной меткой"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.output_text.insert(tk.END, f"{message}\n", tag)
        self.output_text.see(tk.END)
        self.root.update()

    def update_file_info(self):
        filename = self.data_file.get()
        if os.path.exists(filename):
            size = os.path.getsize(filename) / (1024 * 1024)
            self.file_info_label.config(text=f"Файл существует: {size:.1f} МБ", foreground="green")
        else:
            self.file_info_label.config(text="Файл не найден", foreground="red")

    def select_file(self):
        filename = filedialog.askopenfilename(
            title="Выберите CSV файл",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt")]
        )
        if filename:
            self.data_file.set(filename)
            self.update_file_info()
            self.log(f"Выбран файл: {filename}")

    def run_subprocess(self, cmd, timeout=600):
        """Запуск внешней программы с таймаутом"""
        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, encoding='utf-8', errors='replace'
            )
            stdout, stderr = process.communicate(timeout=timeout)
            return process.returncode, stdout, stderr
        except subprocess.TimeoutExpired:
            process.kill()
            return -1, "", "Превышено время ожидания"
        except Exception as e:
            return -1, "", str(e)

    def generate_full_data(self):
        if self.sorting_in_progress:
            return

        def generate():
            self.sorting_in_progress = True
            self.gen_status.config(text="Генерация...", foreground="orange")
            self.log("Начало генерации полного файла (~1.1 ГБ)...", "info")
            self.log("Это может занять несколько минут...", "warning")

            cmd = [sys.executable, 'generate_data.py']
            returncode, stdout, stderr = self.run_subprocess(cmd, timeout=600)

            if returncode == 0:
                self.log("Генерация завершена!", "success")
                self.update_file_info()
                self.gen_status.config(text="Готово", foreground="green")
            else:
                self.log("Ошибка генерации", "error")
                self.gen_status.config(text="Ошибка", foreground="red")

            self.sorting_in_progress = False

        threading.Thread(target=generate, daemon=True).start()

    def generate_test_data(self):
        if self.sorting_in_progress:
            return

        def generate():
            self.sorting_in_progress = True
            self.gen_status.config(text="Генерация тестовых данных...", foreground="orange")
            self.log("Начало генерации тестовых данных (100,000 записей)...", "info")

            cmd = [sys.executable, 'generate_data.py', '--test']
            returncode, stdout, stderr = self.run_subprocess(cmd, timeout=120)

            if returncode == 0:
                self.log("Тестовые данные созданы!", "success")
                self.update_file_info()
                self.gen_status.config(text="Готово", foreground="green")
            else:
                self.log("Ошибка генерации", "error")
                self.gen_status.config(text="Ошибка", foreground="red")

            self.sorting_in_progress = False

        threading.Thread(target=generate, daemon=True).start()

    def compile_cpp(self) -> bool:
        """Компиляция C++ программы"""
        if os.path.exists("external_sort.exe"):
            return True

        self.log("Компиляция C++ программы...", "warning")

        compiler_path = r"C:\msys64\mingw64\bin\g++.exe"
        if not os.path.exists(compiler_path):
            self.log("Компилятор не найден", "error")
            return False

        cmd = [compiler_path, '-O3', '-std=c++17', 'external_sort.cpp', '-o', 'external_sort.exe']
        returncode, stdout, stderr = self.run_subprocess(cmd, timeout=60)

        if returncode == 0 and os.path.exists("external_sort.exe"):
            self.log("Компиляция успешна", "success")
            return True
        else:
            self.log("Ошибка компиляции", "error")
            return False

    def start_sort(self):
        if self.sorting_in_progress:
            messagebox.showwarning("Внимание", "Операция уже выполняется")
            return

        if not os.path.exists(self.data_file.get()):
            messagebox.showerror("Ошибка", "Файл данных не найден")
            return

        if self.language.get() == "cpp" and not self.compile_cpp():
            messagebox.showwarning("Внимание", "Ошибка компиляции C++. Используйте Python.")
            self.language.set("python")

        def sort():
            self.sorting_in_progress = True
            self.sort_btn.config(state="disabled")

            self.log("=" * 60, "info")
            self.log("НАЧАЛО СОРТИРОВКИ", "success")
            self.log(f"Файл: {self.data_file.get()}")
            self.log(f"Язык: {self.language.get().upper()}")

            key_names = ["ID", "ФИО", "Отдел", "Должность", "Зарплата", "Статус", "Дата увольнения"]
            self.log(f"Ключ: {key_names[self.sort_key.get()]}")
            self.log("=" * 60)

            if self.language.get() == "python":
                cmd = [sys.executable, 'external_sort.py',
                       self.data_file.get(), 'sorted.txt', str(self.sort_key.get())]
            else:
                cmd = ['external_sort.exe', self.data_file.get(), 'sorted.txt', str(self.sort_key.get())]

            returncode, stdout, stderr = self.run_subprocess(cmd, timeout=600)

            if stdout:
                for line in stdout.split('\n')[-30:]:
                    if line.strip():
                        self.log(line, "info")

            if returncode == 0:
                self.log("=" * 60, "success")
                self.log("СОРТИРОВКА ЗАВЕРШЕНА!", "success")
                self.log("=" * 60, "success")
            else:
                self.log("=" * 60, "error")
                self.log("ОШИБКА СОРТИРОВКИ", "error")
                self.log("=" * 60, "error")

            self.sorting_in_progress = False
            self.sort_btn.config(state="normal")

        threading.Thread(target=sort, daemon=True).start()

    def verify_sort(self):
        if not os.path.exists("sorted.txt"):
            messagebox.showerror("Ошибка", "Файл sorted.txt не найден")
            return

        self.log("\n" + "=" * 60, "info")
        self.log("ПРОВЕРКА СОРТИРОВКИ", "warning")

        cmd = [sys.executable, 'verify_sort.py', 'sorted.txt', str(self.sort_key.get())]
        returncode, stdout, stderr = self.run_subprocess(cmd, timeout=30)

        if stdout:
            self.log(stdout, "info")
        if stderr:
            self.log(stderr, "error")

    def view_file(self):
        if not os.path.exists("sorted.txt"):
            messagebox.showerror("Ошибка", "Файл sorted.txt не найден")
            return

        self.log(f"\nСодержимое sorted.txt (первые 30 строк):", "info")
        self.log("-" * 60, "info")

        with open('sorted.txt', 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 30:
                    self.log("\n...", "info")
                    break
                self.log(line.strip(), "info")

    def show_statistics(self):
        filename = self.data_file.get()
        if not os.path.exists(filename):
            messagebox.showerror("Ошибка", f"Файл {filename} не найден")
            return

        self.log("\n" + "=" * 60, "info")
        self.log("СТАТИСТИКА ПО ДАННЫМ", "warning")

        import csv
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)

            total = active = fired = 0
            departments = {}
            salary_sum, salary_min, salary_max = 0, float('inf'), 0

            for row in reader:
                total += 1
                if row[5] == 'True':
                    fired += 1
                else:
                    active += 1

                dept = row[2]
                departments[dept] = departments.get(dept, 0) + 1

                salary = int(row[4])
                salary_sum += salary
                salary_min = min(salary_min, salary)
                salary_max = max(salary_max, salary)

        self.log(f"\nВсего сотрудников: {total:,}", "info")
        self.log(f"  - Активных: {active:,} ({active / total * 100:.1f}%)", "success")
        self.log(f"  - Уволенных: {fired:,} ({fired / total * 100:.1f}%)", "error")
        self.log(f"\nСредняя зарплата: {salary_sum / total:,.0f} руб.", "info")
        self.log(f"Диапазон зарплат: {salary_min:,} - {salary_max:,} руб.", "info")

    def show_all_employees(self):
        self.show_employees_by_status(None)

    def show_active_employees(self):
        self.show_employees_by_status(False)

    def show_fired_employees(self):
        self.show_employees_by_status(True)

    def show_employees_by_status(self, show_fired):
        filename = "sorted.txt"
        if not os.path.exists(filename):
            messagebox.showerror("Ошибка", "Файл sorted.txt не найден")
            return

        self.log("\n" + "=" * 90, "info")
        if show_fired is None:
            self.log("ВСЕ СОТРУДНИКИ", "warning")
        elif show_fired:
            self.log("УВОЛЕННЫЕ СОТРУДНИКИ", "error")
        else:
            self.log("АКТИВНЫЕ СОТРУДНИКИ", "success")
        self.log("=" * 90, "info")

        import csv
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)

            self.log(f"{header[0]:<6} {header[1]:<25} {header[2]:<12} {header[3]:<20} "
                     f"{header[4]:<10} {header[5]:<10}", "info")
            self.log("-" * 90, "info")

            # Выводим только первые 50 записей, без подсчета остальных
            count = 0
            for row in reader:
                is_fired = (row[5] == 'True')
                if show_fired is not None and show_fired != is_fired:
                    continue

                status = "Уволен" if is_fired else "Активен"
                self.log(f"{row[0]:<6} {row[1]:<25} {row[2]:<12} {row[3]:<20} "
                         f"{row[4]:<10} {status:<10}", "info")
                count += 1

                if count >= 50:
                    break

            if count == 0:
                self.log("Нет записей, удовлетворяющих условию", "warning")
            elif count == 50:
                self.log("\n... (показаны первые 50 записей)", "info")

            self.log("-" * 90, "info")

    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.log("Вывод очищен", "info")


def main():
    root = tk.Tk()
    app = SortApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()