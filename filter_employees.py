#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Фильтрация сотрудников по статусу занятости
"""

import csv
import sys
import os


class EmployeeFilter:
    """Фильтрует сотрудников по разным критериям"""

    def __init__(self, filename: str):
        self.filename = filename
        self.header = None

    def read_all(self):
        """Читаем все данные из файла"""
        with open(self.filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            data = list(reader)
        return header, data

    def filter_by_status(self, show_fired: bool = None):
        """
        Фильтруем по статусу
        show_fired = True  - только уволенные
        show_fired = False - только активные
        show_fired = None  - все
        """
        _, data = self.read_all()

        if show_fired is None:
            return data

        filtered = []
        for row in data:
            is_fired = (row[5] == 'True')
            if (show_fired and is_fired) or (not show_fired and not is_fired):
                filtered.append(row)

        return filtered

    def print_employees(self, employees, limit: int = 100,
                        show_fired_only: bool = False, show_active_only: bool = False):
        """Выводим сотрудников в виде таблицы"""
        header, _ = self.read_all()

        print(f"\n{'=' * 110}")
        if show_fired_only:
            print("УВОЛЕННЫЕ СОТРУДНИКИ")
        elif show_active_only:
            print("АКТИВНЫЕ СОТРУДНИКИ")
        else:
            print("ВСЕ СОТРУДНИКИ")
        print(f"{'=' * 110}")

        # Заголовки
        print(f"{header[0]:<6} {header[1]:<25} {header[2]:<12} {header[3]:<20} "
              f"{header[4]:<10} {header[5]:<10} {header[6]:<12} {header[7]:<12}")
        print(f"{'-' * 110}")

        # Выводим записи
        for i, row in enumerate(employees[:limit]):
            id_num, name, dept, pos, salary, is_fired, fire_date, hire_date = row

            status = "Уволен" if is_fired == 'True' else "Активен"
            fire_date_display = fire_date if fire_date else "-"

            print(f"{id_num:<6} {name:<25} {dept:<12} {pos:<20} "
                  f"{salary:<10} {status:<10} {fire_date_display:<12} {hire_date:<12}")

        if len(employees) > limit:
            print(f"\n... и еще {len(employees) - limit} записей")

        print(f"{'-' * 110}")
        print(f"Всего показано: {min(len(employees), limit)} из {len(employees)} записей\n")

    def get_statistics(self):
        """Собираем статистику по сотрудникам"""
        _, data = self.read_all()

        stats = {
            'total': 0,
            'active': 0,
            'fired': 0,
            'by_department': {},
            'by_position': {},
            'salary_stats': {'min': float('inf'), 'max': 0, 'sum': 0}
        }

        for row in data:
            stats['total'] += 1

            # Статус
            if row[5] == 'True':
                stats['fired'] += 1
            else:
                stats['active'] += 1

            # Отделы
            dept = row[2]
            stats['by_department'][dept] = stats['by_department'].get(dept, 0) + 1

            # Должности
            pos = row[3]
            stats['by_position'][pos] = stats['by_position'].get(pos, 0) + 1

            # Зарплаты
            salary = int(row[4])
            stats['salary_stats']['min'] = min(stats['salary_stats']['min'], salary)
            stats['salary_stats']['max'] = max(stats['salary_stats']['max'], salary)
            stats['salary_stats']['sum'] += salary

        stats['salary_stats']['avg'] = stats['salary_stats']['sum'] / stats['total']

        return stats

    def print_statistics(self):
        """Выводим статистику красиво"""
        stats = self.get_statistics()

        print(f"\n{'=' * 60}")
        print("СТАТИСТИКА ПО СОТРУДНИКАМ")
        print(f"{'=' * 60}")
        print(f"Всего сотрудников: {stats['total']:,}")
        print(f"  - Активных: {stats['active']:,} ({stats['active'] / stats['total'] * 100:.1f}%)")
        print(f"  - Уволенных: {stats['fired']:,} ({stats['fired'] / stats['total'] * 100:.1f}%)")

        print(f"\nЗарплата:")
        print(f"  - Минимальная: {stats['salary_stats']['min']:,} руб.")
        print(f"  - Максимальная: {stats['salary_stats']['max']:,} руб.")
        print(f"  - Средняя: {stats['salary_stats']['avg']:,.0f} руб.")

        print(f"\nПо отделам:")
        for dept, count in sorted(stats['by_department'].items()):
            print(f"  {dept}: {count:,} чел. ({count / stats['total'] * 100:.1f}%)")

        print(f"\nПо должностям (Топ-10):")
        sorted_positions = sorted(stats['by_position'].items(), key=lambda x: x[1], reverse=True)
        for pos, count in sorted_positions[:10]:
            print(f"  {pos}: {count:,} чел.")

        print(f"{'=' * 60}\n")


def main():
    """Запуск из командной строки"""
    filename = "sorted.txt" if len(sys.argv) < 2 else sys.argv[1]

    if not os.path.exists(filename):
        print(f"Файл {filename} не найден!")
        print("Сначала выполните сортировку.")
        sys.exit(1)

    filter_tool = EmployeeFilter(filename)

    # Интерактивное меню
    while True:
        print("\n" + "=" * 50)
        print("ФИЛЬТРАЦИЯ СОТРУДНИКОВ")
        print("=" * 50)
        print("1. Показать всех сотрудников")
        print("2. Показать только активных")
        print("3. Показать только уволенных")
        print("4. Показать статистику")
        print("5. Выйти")
        print("-" * 50)

        choice = input("Выберите действие (1-5): ").strip()

        if choice == '1':
            employees = filter_tool.filter_by_status(show_fired=None)
            filter_tool.print_employees(employees, show_fired_only=False, show_active_only=False)

        elif choice == '2':
            employees = filter_tool.filter_by_status(show_fired=False)
            filter_tool.print_employees(employees, show_active_only=True)

        elif choice == '3':
            employees = filter_tool.filter_by_status(show_fired=True)
            filter_tool.print_employees(employees, show_fired_only=True)

        elif choice == '4':
            filter_tool.print_statistics()

        elif choice == '5':
            print("До свидания!")
            break

        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()