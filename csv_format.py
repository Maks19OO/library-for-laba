import csv
import os
from datetime import datetime

from .exceptions import ColumnError, FileError
from .table import Table
from .type_detect import apply_detected_types, detect_column_types


def _cell_to_str(val):
    if val is None:
        return ""
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(val, bool):
        return "true" if val else "false"
    return str(val)


def _read_one(path):
    if not os.path.isfile(path):
        raise FileError(f"файл не найден: {path}")
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except StopIteration:
            raise FileError(f"пустой файл: {path}")
        rows = []
        for row in reader:
            cells = [None if c == "" else c for c in row]
            while len(cells) < len(headers):
                cells.append(None)
            rows.append(cells[: len(headers)])
    return headers, rows


def load_table(*paths, auto_types=False):
    if not paths:
        raise FileError("не указан файл")
    headers, rows = _read_one(paths[0])
    for path in paths[1:]:
        h2, r2 = _read_one(path)
        if h2 != headers:
            raise ColumnError(f"разные столбцы в {path}")
        rows.extend(r2)
    table = Table(headers=headers, rows=rows)
    if auto_types:
        apply_detected_types(table)
    return table


def _part_path(path, part):
    base, ext = os.path.splitext(path)
    if part == 0:
        return path
    return f"{base}_part{part}{ext}"


def save_table(path, table, max_rows=None):
    if max_rows is not None:
        if max_rows < 1:
            raise FileError("max_rows должен быть >= 1")
        paths = []
        rows = table._row_lists()
        part = 0
        for start in range(0, len(rows), max_rows):
            chunk = Table(
                headers=list(table.headers),
                rows=rows[start : start + max_rows],
                types=dict(table._types),
            )
            p = _part_path(path, part)
            save_table(p, chunk)
            paths.append(p)
            part += 1
        return paths
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(table.headers)
        for row in table._row_lists():
            w.writerow([_cell_to_str(row[i] if i < len(row) else None) for i in range(len(table.headers))])
    return path
