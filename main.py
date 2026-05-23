#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Главный модуль для запуска лабораторной работы 5.1
Предметная область: База данных сотрудников компании
"""

import sys
import os
import argparse


def print_banner():
    """Вывод баннера"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║     Лабораторная работа 5.1: Внешняя сортировка больших файлов   ║
    ║                  База данных сотрудников компании                ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description='Внешняя сортировка больших файлов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Запуск GUI приложения
  python main.py --gui

  # Генерация данных
  python main.py --generate

  # Сортировка (Python)
  python main.py --sort --input data.csv --output sorted.txt --key 0 --lang python

  # Сортировка (C++)
  python main.py --sort --input data.csv --output sorted.txt --key 4 --lang cpp

  # Фильтрация
  python main.py --filter --file sorted.txt --active

  # Проверка
  python main.py --verify --file sorted.txt --key 0
        """
    )

    parser.add_argument('--gui', action='store_true', help='Запуск GUI приложения')
    parser.add_argument('--generate', action='store_true', help='Генерация данных')
    parser.add_argument('--test', action='store_true', help='Генерация тестовых данных')
    parser.add_argument('--sort', action='store_true', help='Запуск сортировки')
    parser.add_argument('--input', default='data.csv', help='Входной файл')
    parser.add_argument('--output', default='sorted.txt', help='Выходной файл')
    parser.add_argument('--key', type=int, default=0, choices=range(7),
                        help='Ключ сортировки (0-6)')
    parser.add_argument('--lang', choices=['python', 'cpp'], default='python',
                        help='Язык реализации')
    parser.add_argument('--filter', action='store_true', help='Фильтрация сотрудников')
    parser.add_argument('--file', default='sorted.txt', help='Файл для фильтрации')
    parser.add_argument('--active', action='store_true', help='Показать активных')
    parser.add_argument('--fired', action='store_true', help='Показать уволенных')
    parser.add_argument('--verify', action='store_true', help='Проверка сортировки')

    args = parser.parse_args()

    print_banner()

    # GUI
    if args.gui:
        from gui_app import main as gui_main
        gui_main()
        return

    # Генерация данных
    if args.generate:
        from generate_data import EmployeeDataGenerator
        generator = EmployeeDataGenerator()
        generator.generate_file(args.input)
        return

    if args.test:
        from generate_data import generate_test_data
        generate_test_data(args.input)
        return

    # Сортировка
    if args.sort:
        if args.lang == 'python':
            from external_sort import ExternalSortPython
            sorter = ExternalSortPython(args.input, args.output, args.key)
            sorter.sort()
        else:
            # Запуск C++ программы
            import subprocess
            if not os.path.exists('external_sort.exe'):
                print("Компиляция C++ программы...")
                subprocess.run(['g++', '-O3', '-std=c++17', 'external_sort.cpp', '-o', 'external_sort.exe'],
                               check=True)
            subprocess.run(['./external_sort.exe', args.input, args.output, str(args.key)])
        return

    # Фильтрация
    if args.filter:
        from filter_employees import EmployeeFilter
        filter_tool = EmployeeFilter(args.file)

        if args.active:
            employees = filter_tool.filter_by_status(show_fired=False)
            filter_tool.print_employees(employees, show_active_only=True)
        elif args.fired:
            employees = filter_tool.filter_by_status(show_fired=True)
            filter_tool.print_employees(employees, show_fired_only=True)
        else:
            employees = filter_tool.filter_by_status(show_fired=None)
            filter_tool.print_employees(employees)

        filter_tool.print_statistics()
        return

    # Проверка
    if args.verify:
        from verify_sort import SortVerifier
        verifier = SortVerifier(args.file, args.key)
        verifier.print_verification_result()
        verifier.print_sample(20)
        return

    # Если ничего не выбрано, показываем справку
    parser.print_help()


if __name__ == "__main__":
    main()