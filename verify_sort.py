#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка правильности сортировки
"""

import csv
import sys
import os


class SortVerifier:
    """Проверяет отсортирован ли файл"""

    # Соответствие номеров ключей и названий полей
    SORT_KEYS = {
        0: 'id',
        1: 'full_name',
        2: 'department',
        3: 'position',
        4: 'salary',
        5: 'is_fired',
        6: 'fire_date'
    }

    def __init__(self, filename: str, sort_key: int = 0):
        self.filename = filename
        self.sort_key = sort_key
        self.header = None
        self.data = None

    def load_data(self, limit: int = None):
        """Загружаем данные из файла, можно ограничить количество"""
        with open(self.filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            self.header = next(reader)

            if limit:
                self.data = []
                for i, row in enumerate(reader):
                    if i >= limit:
                        break
                    self.data.append(row)
            else:
                self.data = list(reader)

    def get_value(self, row):
        """Берем значение по выбранному ключу сортировки"""
        val = row[self.sort_key]

        # Для чисел преобразуем в int, для статуса в boolean
        if self.sort_key == 0 or self.sort_key == 4:  # id или salary
            return int(val) if val else 0
        elif self.sort_key == 5:  # is_fired
            return val == 'True'
        else:
            return val

    def verify(self, limit: int = 10000):
        """
        Проверяем что записи идут по возрастанию
        Возвращает: (отсортирован_ли, номер_строки, предыдущее, текущее)
        """
        self.load_data(limit)

        if not self.data:
            return True, 0, None, None

        prev_value = self.get_value(self.data[0])

        for i, row in enumerate(self.data[1:], start=2):
            curr_value = self.get_value(row)

            try:
                if curr_value < prev_value:
                    return False, i, prev_value, curr_value
            except TypeError:
                if str(curr_value) < str(prev_value):
                    return False, i, prev_value, curr_value

            prev_value = curr_value

        return True, 0, None, None

    def print_verification_result(self, limit: int = 10000):
        """Выводим результат проверки"""
        print(f"\n{'=' * 60}")
        print("ПРОВЕРКА ПРАВИЛЬНОСТИ СОРТИРОВКИ")
        print(f"{'=' * 60}")
        print(f"Файл: {self.filename}")
        print(f"Ключ сортировки: {self.SORT_KEYS[self.sort_key]}")

        is_sorted, position, prev_val, curr_val = self.verify(limit)

        if is_sorted:
            print(f"\nФайл правильно отсортирован по ключу '{self.SORT_KEYS[self.sort_key]}'")
        else:
            print(f"\nОШИБКА: Файл отсортирован НЕПРАВИЛЬНО!")
            print(f"   Нарушение на строке {position}")
            print(f"   Предыдущее значение: {prev_val}")
            print(f"   Текущее значение: {curr_val}")

        print(f"{'=' * 60}\n")

    def print_sample(self, num_rows: int = 20):
        """Показываем первые строки файла"""
        print(f"\n{'=' * 80}")
        print(f"ПЕРВЫЕ {num_rows} ЗАПИСЕЙ ФАЙЛА")
        print(f"{'=' * 80}")

        with open(self.filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)

            # Шапка таблицы
            print(f"{header[0]:<6} {header[1]:<25} {header[2]:<12} {header[3]:<20} "
                  f"{header[4]:<10} {header[5]:<10} {header[6]:<12} {header[7]:<12}")
            print(f"{'-' * 80}")

            # Выводим данные
            for i, row in enumerate(reader):
                if i >= num_rows:
                    print(f"\n... и еще строки")
                    break

                id_num, name, dept, pos, salary, is_fired, fire_date, hire_date = row
                status = "Уволен" if is_fired == 'True' else "Активен"
                fire_date_display = fire_date if fire_date else "-"

                print(f"{id_num:<6} {name:<25} {dept:<12} {pos:<20} "
                      f"{salary:<10} {status:<10} {fire_date_display:<12} {hire_date:<12}")

        print(f"{'=' * 80}\n")


def main():
    """Запуск из командной строки"""
    filename = "sorted.txt" if len(sys.argv) < 2 else sys.argv[1]
    sort_key = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    if not os.path.exists(filename):
        print(f"Файл {filename} не найден!")
        sys.exit(1)

    verifier = SortVerifier(filename, sort_key)

    print("\nМЕНЮ ПРОВЕРКИ:")
    print("1. Проверить сортировку")
    print("2. Показать первые строки")
    print("3. Полная проверка (все записи)")

    choice = input("\nВыберите действие (1-3): ").strip()

    if choice == '1':
        verifier.print_verification_result(limit=10000)
    elif choice == '2':
        verifier.print_sample(20)
    elif choice == '3':
        verifier.print_verification_result(limit=None)
    else:
        print("Неверный выбор")


if __name__ == "__main__":
    main()