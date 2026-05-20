import os
import pickle

from .exceptions import ColumnError, FileError
from .table import Table
from .type_detect import apply_detected_types


def load_table(*paths, auto_types=False):
    if not paths:
        raise FileError("не указан файл")
    tables = []
    for path in paths:
        if not os.path.isfile(path):
            raise FileError(f"файл не найден: {path}")
        with open(path, "rb") as f:
            data = pickle.load(f)
        if isinstance(data, Table):
            tables.append(data)
        elif isinstance(data, dict):
            tables.append(Table.from_dict(data))
        else:
            raise FileError(f"неизвестный формат в {path}")
    result = tables[0].copy()
    for t in tables[1:]:
        if t.headers != result.headers:
            raise ColumnError("разные столбцы в файлах")
        for row in t._row_lists():
            result.rows.append(list(row))
    if auto_types:
        apply_detected_types(result)
    return result


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
    data = {
        "headers": list(table.headers),
        "rows": table._row_lists(),
        "types": {k: v for k, v in table._types.items()},
    }
    with open(path, "wb") as f:
        pickle.dump(data, f)
    return path
