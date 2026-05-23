#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор данных для лабораторной работы
Создает CSV файл с сотрудниками компании
"""

import csv
import random
import os
import time
from datetime import datetime, timedelta


class EmployeeDataGenerator:
    """Генератор данных о сотрудниках"""

    def __init__(self):
        # Список имен и фамилий для реалистичности
        self.first_names = [
            'Иван', 'Петр', 'Сидор', 'Алексей', 'Дмитрий', 'Михаил', 'Андрей',
            'Сергей', 'Владимир', 'Николай', 'Елена', 'Мария', 'Анна', 'Ольга',
            'Татьяна', 'Наталья', 'Ирина', 'Светлана', 'Екатерина', 'Юлия'
        ]

        self.last_names = [
            'Иванов', 'Петров', 'Сидоров', 'Кузнецов', 'Смирнов', 'Васильев',
            'Михайлов', 'Новиков', 'Федоров', 'Морозов', 'Волкова', 'Кузнецова',
            'Попова', 'Соколова', 'Лебедева', 'Козлова', 'Новикова', 'Зайцев'
        ]

        # Отделы компании
        self.departments = ['IT', 'HR', 'Sales', 'Marketing', 'Finance', 'R&D', 'Logistics', 'Legal']

        # Какие должности в каких отделах бывают
        self.positions_by_dept = {
            'IT': ['Junior Developer', 'Middle Developer', 'Senior Developer', 'Team Lead', 'DevOps', 'CTO'],
            'HR': ['HR Specialist', 'HR Manager', 'Recruiter', 'HR Director'],
            'Sales': ['Sales Representative', 'Account Manager', 'Sales Manager', 'VP of Sales'],
            'Marketing': ['Marketing Specialist', 'PR Manager', 'Marketing Manager', 'CMO'],
            'Finance': ['Accountant', 'Financial Analyst', 'Finance Manager', 'CFO'],
            'R&D': ['Researcher', 'Data Scientist', 'ML Engineer', 'R&D Director'],
            'Logistics': ['Logistics Coordinator', 'Supply Manager', 'Warehouse Manager'],
            'Legal': ['Legal Counsel', 'Corporate Lawyer', 'Legal Director']
        }

        # Зарплаты в зависимости от уровня должности
        self.salary_ranges = {
            'Junior': (40000, 70000),
            'Middle': (70000, 110000),
            'Senior': (110000, 160000),
            'Lead': (140000, 200000),
            'Manager': (90000, 150000),
            'Director': (150000, 250000),
            'Default': (40000, 120000)
        }

    def get_position_level(self, position: str) -> str:
        """Определяем уровень по названию должности"""
        if 'Junior' in position:
            return 'Junior'
        elif 'Middle' in position:
            return 'Middle'
        elif 'Senior' in position:
            return 'Senior'
        elif 'Lead' in position:
            return 'Lead'
        elif 'Manager' in position:
            return 'Manager'
        elif 'Director' in position or 'CTO' in position or 'CFO' in position:
            return 'Director'
        else:
            return 'Default'

    def get_salary_for_position(self, position: str) -> int:
        """Выдаем зарплату в зависимости от должности"""
        level = self.get_position_level(position)
        min_salary, max_salary = self.salary_ranges.get(level, self.salary_ranges['Default'])
        return random.randint(min_salary, max_salary)

    def generate_full_name(self) -> str:
        """Склеиваем фамилию и имя"""
        return f"{random.choice(self.last_names)} {random.choice(self.first_names)}"

    def generate_date(self, years_ago_max: int, years_ago_min: int = 0) -> str:
        """Генерируем случайную дату за последние years_ago_max лет"""
        days_ago = random.randint(years_ago_min * 365, years_ago_max * 365)
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime('%Y-%m-%d')

    def generate_employee(self, emp_id: int) -> dict:
        """Создаем одного сотрудника со всеми полями"""
        # Выбираем отдел и должность
        department = random.choice(self.departments)
        position = random.choice(self.positions_by_dept[department])
        salary = self.get_salary_for_position(position)
        full_name = self.generate_full_name()

        # Дата приема (от 0 до 10 лет назад)
        hire_years_ago = random.randint(0, 10)
        hire_date = self.generate_date(hire_years_ago, 0)

        # 12% вероятность что сотрудник уволен
        is_fired = random.random() < 0.12

        # Если уволен, генерируем дату увольнения
        fire_date = ''
        if is_fired and hire_years_ago > 0:
            years_employed = random.randint(1, max(1, hire_years_ago))
            fire_date = self.generate_date(years_employed, 0)

        return {
            'id': emp_id,
            'full_name': full_name,
            'department': department,
            'position': position,
            'salary': salary,
            'is_fired': 'True' if is_fired else 'False',
            'fire_date': fire_date,
            'hire_date': hire_date
        }

    def generate_file(self, filename: str, target_size_mb: int = 1126):
        """Главная функция - генерируем файл нужного размера"""

        target_size_bytes = target_size_mb * 1024 * 1024

        print(f"\n{'=' * 60}")
        print(f"ГЕНЕРАЦИЯ ДАННЫХ")
        print(f"{'=' * 60}")
        print(f"Файл: {filename}")
        print(f"Нужно сделать: {target_size_mb} МБ")
        print(f"{'=' * 60}\n")

        start_time = time.time()
        row_count = 0
        stats = {'fired': 0, 'active': 0, 'by_department': {}}

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Пишем шапку таблицы
            writer.writerow(['id', 'full_name', 'department', 'position', 'salary',
                             'is_fired', 'fire_date', 'hire_date'])

            last_progress = 0

            # Генерируем пока не достигнем нужного размера
            while True:
                employee = self.generate_employee(row_count + 1)
                writer.writerow([
                    employee['id'], employee['full_name'], employee['department'],
                    employee['position'], employee['salary'], employee['is_fired'],
                    employee['fire_date'], employee['hire_date']
                ])
                row_count += 1

                # Собираем статистику
                if employee['is_fired'] == 'True':
                    stats['fired'] += 1
                else:
                    stats['active'] += 1
                stats['by_department'][employee['department']] = \
                    stats['by_department'].get(employee['department'], 0) + 1

                # Каждые 5000 строк проверяем размер
                if row_count % 5000 == 0:
                    current_size = f.tell()
                    progress = (current_size / target_size_bytes) * 100

                    # Показываем прогресс каждый процент
                    if progress - last_progress >= 1:
                        elapsed = time.time() - start_time
                        if progress > 0:
                            remaining = (elapsed / progress) * (100 - progress)
                        else:
                            remaining = 0

                        print(f"Прогресс: {progress:.1f}% | "
                              f"Размер: {current_size // (1024 * 1024)}/{target_size_mb} МБ | "
                              f"Записей: {row_count:,} | "
                              f"Осталось: {remaining:.0f} сек")
                        last_progress = progress

                    # Хватит, достигли нужного размера
                    if current_size >= target_size_bytes:
                        print(f"\nГотово! Достигли нужного размера.")
                        break

            final_size = f.tell()

        elapsed = time.time() - start_time

        # Выводим итоговую статистику
        print(f"\n{'=' * 60}")
        print(f"ГЕНЕРАЦИЯ ЗАВЕРШЕНА")
        print(f"{'=' * 60}")
        print(f"Всего записей: {row_count:,}")
        print(f"  - Активных: {stats['active']:,} ({stats['active'] / row_count * 100:.1f}%)")
        print(f"  - Уволенных: {stats['fired']:,} ({stats['fired'] / row_count * 100:.1f}%)")
        print(f"\nПо отделам:")
        for dept, count in sorted(stats['by_department'].items()):
            print(f"  {dept}: {count:,} чел. ({count / row_count * 100:.1f}%)")
        print(f"\nРазмер файла: {final_size / (1024 * 1024):.1f} МБ")
        print(f"Время: {elapsed:.2f} сек")
        print(f"{'=' * 60}\n")

        return row_count, stats


def generate_test_data(filename: str, num_records: int = 100000):
    """Для быстрого тестирования - генерируем 100к записей"""

    generator = EmployeeDataGenerator()

    print(f"\n{'=' * 60}")
    print(f"ГЕНЕРАЦИЯ ТЕСТОВЫХ ДАННЫХ")
    print(f"{'=' * 60}")
    print(f"Файл: {filename}")
    print(f"Создаем {num_records:,} записей")
    print(f"{'=' * 60}\n")

    start_time = time.time()

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'full_name', 'department', 'position', 'salary',
                         'is_fired', 'fire_date', 'hire_date'])

        for i in range(num_records):
            employee = generator.generate_employee(i + 1)
            writer.writerow([
                employee['id'], employee['full_name'], employee['department'],
                employee['position'], employee['salary'], employee['is_fired'],
                employee['fire_date'], employee['hire_date']
            ])

            # Каждые 20000 строк показываем прогресс
            if (i + 1) % 20000 == 0:
                print(f"  Создано {i + 1:,} записей...")

    elapsed = time.time() - start_time
    file_size = os.path.getsize(filename) / (1024 * 1024)

    print(f"\nТестовые данные готовы!")
    print(f"  Записей: {num_records:,}")
    print(f"  Размер: {file_size:.1f} МБ")
    print(f"  Время: {elapsed:.2f} сек\n")


if __name__ == "__main__":
    import sys

    # Если запустили с ключом --test, делаем тестовый файл
    # Иначе генерируем полный файл на 1.1 ГБ
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        generate_test_data("data.csv", num_records=100000)
    else:
        generator = EmployeeDataGenerator()
        generator.generate_file("data.csv", target_size_mb=1126)