# library-for-laba

Библиотека для работы с табличными данными: создание таблиц, типизация столбцов, фильтрация и объединение, арифметика по столбцам, загрузка и сохранение в CSV, pickle и текстовом виде.

**Автор:** ММБ ДИРПО25-1с

## Установка

После публикации на PyPI:

```bash
pip install library-for-laba
```

Локально из репозитория (из корня проекта):

```bash
pip install .
```

Требуется Python 3.10+.

## Быстрый старт

```python
from library_for_laba.table import Table
from library_for_laba import operations, arithmetic, csv_format

# Создание таблицы
table = Table(
    headers=["id", "name", "score"],
    rows=[
        [1, "Анна", 90],
        [2, "Борис", 85],
        [3, "Вера", 92],
    ],
    types={"id": int, "name": str, "score": int},
)

# Вывод в консоль
table.print_table()
```

## Класс Table

Основной тип данных — `Table` с заголовками, строками и типами столбцов.

Поддерживаемые типы: `int`, `float`, `bool`, `str`, `datetime` (можно передать как тип Python или строкой: `"int"`, `"float"`, `"bool"`, `"str"`, `"datetime"`).

```python
from datetime import datetime

table = Table(
    headers=["date", "active", "value"],
    rows=[["2024-01-15", "да", "3.14"]],
    types={"date": datetime, "active": bool, "value": float},
)
```

### Методы Table

| Метод | Описание |
|-------|----------|
| `print_table(file=None)` | Печать таблицы в консоль или в файл |
| `get_rows_by_number(start, stop=None, copy_table=False)` | Срез строк по номерам |
| `get_rows_by_index(*vals, copy_table=False)` | Строки, где значение в первом столбце совпадает с переданными |
| `get_column_types(by_number=True)` | Словарь типов столбцов |
| `set_column_types(types_dict, by_number=True)` | Задать типы столбцов |
| `get_values(column=0)` | Список значений столбца |
| `get_value(column=0)` | Значение столбца (таблица из одной строки) |
| `set_values(values, column=0)` | Записать список значений в столбец |
| `set_value(value, column=0)` | Записать одно значение (одна строка) |
| `copy()` | Глубокая копия |
| `to_dict()` / `from_dict(d)` | Сериализация в словарь |

Столбец можно указывать по индексу (`0`, `1`, …) или по имени заголовка (`"name"`).

## Операции с таблицами

Модуль `operations`:

```python
from library_for_laba import operations

# Объединить две таблицы с одинаковыми заголовками
merged = operations.concat(table1, table2)

# Разделить по номеру строки
left, right = operations.split(table, row_number=2)

# Фильтр по списку True/False
filtered = operations.filter_rows(table, [True, False, True])

# Слияние двух таблиц
result = operations.merge_tables(
    table1,
    table2,
    by_number=True,      # по номеру строки; False — по первому столбцу (индекс)
    fill_none=True,      # заполнять отсутствующие ячейки None
    on_conflict="left",  # "left", "right" или "raise"
)
```

## Арифметика и сравнение

Модуль `arithmetic` — операции по столбцам (результат записывается в новый или указанный столбец):

```python
from library_for_laba import arithmetic

arithmetic.add(table, "a", "b")           # a + b
arithmetic.sub(table, "a", "b")           # a - b
arithmetic.mul(table, "a", "b")           # a * b
arithmetic.div(table, "a", "b")           # a / b

# Сравнение — возвращает список bool по строкам
flags = arithmetic.gr(table, "score", 80)  # score > 80
flags = arithmetic.eq(table, "name", "Анна")
```

Доступны: `eq`, `ne`, `gr`, `ls`, `ge`, `le`.

## Файлы

### CSV

```python
from library_for_laba import csv_format

# Загрузка (несколько файлов — склейка при одинаковых заголовках)
table = csv_format.load_table("data.csv", auto_types=True)

# Сохранение
csv_format.save_table("out.csv", table)

# Разбиение на части (data_part1.csv, data_part2.csv, …)
csv_format.save_table("data.csv", table, max_rows=1000)
```

### Pickle

```python
from library_for_laba import pickle_format

table = pickle_format.load_table("data.pkl", auto_types=True)
pickle_format.save_table("data.pkl", table)
pickle_format.save_table("data.pkl", table, max_rows=500)
```

### Текстовая таблица (ASCII)

```python
from library_for_laba import text_format

text_format.save_table("table.txt", table)
```

## Автоопределение типов

```python
from library_for_laba.type_detect import detect_column_types, apply_detected_types

types = detect_column_types(table)   # {0: int, 1: str, ...}
apply_detected_types(table)          # применить типы и преобразовать значения
```

Параметр `auto_types=True` в `load_table` для CSV и pickle делает то же самое при загрузке.

## Исключения

| Исключение | Когда возникает |
|------------|-----------------|
| `ColumnError` | Неверный столбец, разные заголовки |
| `RowError` | Неверный индекс строки, пустая таблица |
| `TableTypeError` | Неизвестный или несовместимый тип |
| `TableValueError` | Значение не приводится к типу столбца |
| `FileError` | Файл не найден, пустой файл |
| `MergeError` | Ошибки при слиянии |

Все наследуются от `TableError` (`library_for_laba.exceptions`).

## Пример: полный цикл

```python
from library_for_laba.table import Table
from library_for_laba import csv_format, arithmetic, operations

table = csv_format.load_table("students.csv", auto_types=True)

# Оставить только оценки выше 70
high = operations.filter_rows(
    table,
    arithmetic.gr(table, "score", 70),
    copy_table=True,
)

high.print_table()
csv_format.save_table("top_students.csv", high)
```

## Лицензия

Учебный проект (лабораторная работа).
