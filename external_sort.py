#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Внешняя сортировка на Python
Сортирует большие файлы, которые не помещаются в память
"""

import csv
import os
import tempfile
import shutil
import heapq
import time
import sys


class ExternalSortPython:
    """Класс для внешней сортировки"""

    # Какому ключу какой номер соответствует
    SORT_KEYS = {
        0: ('id', 'int'),
        1: ('full_name', 'str'),
        2: ('department', 'str'),
        3: ('position', 'str'),
        4: ('salary', 'int'),
        5: ('is_fired', 'str'),
        6: ('fire_date', 'str')
    }

    def __init__(self, input_file: str, output_file: str = "sorted.txt", sort_key: int = 0):
        self.input_file = input_file
        self.output_file = output_file
        self.sort_key = sort_key
        self.temp_dir = None
        self.temp_files = []

        # Собираем статистику
        self.stats = {
            'file_size': 0,
            'memory_limit': 0,
            'num_chunks': 0,
            'split_time': 0,
            'merge_time': 0,
            'total_time': 0,
            'records_count': 0
        }

        # Размер файла и лимит памяти (10%)
        self.stats['file_size'] = os.path.getsize(input_file)
        self.stats['memory_limit'] = self.stats['file_size'] // 10

        print(f"\n{'=' * 60}")
        print(f"ВНЕШНЯЯ СОРТИРОВКА (PYTHON)")
        print(f"{'=' * 60}")
        print(f"Входной файл: {input_file}")
        print(f"Выходной файл: {output_file}")
        print(f"Ключ сортировки: {self.SORT_KEYS[sort_key][0]}")
        print(f"Размер файла: {self.stats['file_size'] / (1024 * 1024):.1f} МБ")
        print(f"Лимит памяти (10%): {self.stats['memory_limit'] / (1024 * 1024):.1f} МБ")
        print(f"{'=' * 60}\n")

    def __del__(self):
        """При удалении объекта чистим временные файлы"""
        self.cleanup()

    def cleanup(self):
        """Удаляем временные файлы и папку"""
        if self.temp_files:
            for temp_file in self.temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass

        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass

    def get_key_func(self):
        """Возвращает функцию, которая достает значение для сортировки"""
        key_name, key_type = self.SORT_KEYS[self.sort_key]

        def key_func(row):
            value = row[self.sort_key]
            if key_type == 'int':
                return int(value) if value else 0
            elif key_type == 'str':
                return value if value else ''
            return value

        return key_func

    def read_chunks(self):
        """Читаем файл блоками по 10% от размера"""
        chunk = []
        chunk_memory = 0

        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # запоминаем заголовок

            for row in reader:
                # Примерно считаем сколько памяти занимает строка
                row_size = sum(len(str(cell)) for cell in row)
                chunk_memory += row_size
                chunk.append(row)

                # Если набрали лимит - отдаем чанк
                if chunk_memory >= self.stats['memory_limit']:
                    yield header, chunk
                    chunk = []
                    chunk_memory = 0

            # Последний чанк
            if chunk:
                yield header, chunk

    def sort_and_write_chunk(self, header, chunk, chunk_idx):
        """Сортируем чанк и сохраняем во временный файл"""
        key_func = self.get_key_func()
        chunk.sort(key=key_func)

        temp_file = os.path.join(self.temp_dir, f"chunk_{chunk_idx:04d}.csv")

        with open(temp_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(chunk)

        return temp_file

    def split_phase(self):
        """Фаза разбиения: читаем, сортируем, сохраняем"""
        print("ФАЗА 1: РАЗБИЕНИЕ")
        print("-" * 40)

        start_time = time.time()

        # Создаем временную папку
        self.temp_dir = tempfile.mkdtemp(prefix="ext_sort_py_")

        chunk_count = 0
        # Считаем количество записей
        records_count = 0

        for header, chunk in self.read_chunks():
            temp_file = self.sort_and_write_chunk(header, chunk, chunk_count)
            self.temp_files.append(temp_file)
            records_count += len(chunk)
            chunk_count += 1

            if chunk_count % 10 == 0:
                print(f"  Создано чанков: {chunk_count}")

        elapsed = time.time() - start_time
        self.stats['split_time'] = elapsed
        self.stats['num_chunks'] = chunk_count
        self.stats['records_count'] = records_count

        print(f"  Создано {chunk_count} чанков")
        print(f"  Время разбиения: {elapsed:.2f} сек\n")

        return chunk_count

    def merge_phase(self):
        """Фаза слияния: объединяем чанки в один файл через кучу"""
        print("ФАЗА 2: СЛИЯНИЕ")
        print("-" * 40)

        start_time = time.time()

        if not self.temp_files:
            raise ValueError("Нет временных файлов для слияния")

        files = []
        readers = []

        try:
            # Открываем все временные файлы
            for temp_file in self.temp_files:
                f = open(temp_file, 'r', encoding='utf-8')
                reader = csv.reader(f)
                header = next(reader)  # заголовок читаем, он одинаковый во всех
                files.append(f)
                readers.append(reader)

            key_func = self.get_key_func()

            # Создаем кучу из первых записей
            heap = []
            for idx, reader in enumerate(readers):
                try:
                    row = next(reader)
                    heapq.heappush(heap, (key_func(row), idx, row))
                except StopIteration:
                    pass

            # Пишем результат
            with open(self.output_file, 'w', newline='', encoding='utf-8') as out_f:
                writer = csv.writer(out_f)
                writer.writerow(header)

                output_count = 0
                while heap:
                    _, idx, row = heapq.heappop(heap)
                    writer.writerow(row)
                    output_count += 1

                    if output_count % 50000 == 0:
                        print(f"  Записано записей: {output_count:,}")

                    # Берем следующую запись из того же файла
                    try:
                        next_row = next(readers[idx])
                        heapq.heappush(heap, (key_func(next_row), idx, next_row))
                    except StopIteration:
                        pass

            print(f"  Записано {output_count:,} записей")

        finally:
            for f in files:
                f.close()

        elapsed = time.time() - start_time
        self.stats['merge_time'] = elapsed

        print(f"  Время слияния: {elapsed:.2f} сек\n")

    def sort(self):
        """Запускаем сортировку"""
        total_start = time.time()

        try:
            num_chunks = self.split_phase()

            if num_chunks == 0:
                raise ValueError("Нет данных для сортировки")

            self.merge_phase()

        except Exception as e:
            print(f"Ошибка при сортировке: {e}")
            raise
        finally:
            self.cleanup()

        total_elapsed = time.time() - total_start
        self.stats['total_time'] = total_elapsed

        # Выводим итоги
        self.print_statistics()

        return self.stats

    def print_statistics(self):
        """Печатаем статистику"""
        print(f"\n{'=' * 60}")
        print(f"ИТОГОВАЯ СТАТИСТИКА")
        print(f"{'=' * 60}")
        print(f"Всего записей: {self.stats['records_count']:,}")
        print(f"Количество чанков: {self.stats['num_chunks']}")
        print(f"Время разбиения: {self.stats['split_time']:.2f} сек")
        print(f"Время слияния: {self.stats['merge_time']:.2f} сек")
        print(f"Общее время: {self.stats['total_time']:.2f} сек")

        if self.stats['total_time'] < 600:
            print(f"\nВремя сортировки в пределах нормы (менее 10 минут)")
        else:
            print(f"\nВремя сортировки превышает 10 минут!")

        print(f"{'=' * 60}\n")


def main():
    """Запуск из командной строки"""
    if len(sys.argv) < 2:
        print("Использование: python external_sort.py <input_file> [output_file] [sort_key]")
        print("\nПараметры:")
        print("  input_file  - входной CSV файл")
        print("  output_file - выходной файл (по умолчанию: sorted.txt)")
        print("  sort_key    - ключ сортировки:")
        print("                0 - id")
        print("                1 - full_name")
        print("                2 - department")
        print("                3 - position")
        print("                4 - salary")
        print("                5 - is_fired")
        print("                6 - fire_date")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "sorted.txt"
    sort_key = int(sys.argv[3]) if len(sys.argv) > 3 else 0

    if sort_key not in ExternalSortPython.SORT_KEYS:
        print(f"Ошибка: Неверный ключ сортировки {sort_key}")
        print(f"Допустимые значения: {list(ExternalSortPython.SORT_KEYS.keys())}")
        sys.exit(1)

    sorter = ExternalSortPython(input_file, output_file, sort_key)
    sorter.sort()


if __name__ == "__main__":
    main()