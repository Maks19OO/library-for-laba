from datetime import datetime

from .exceptions import TableTypeError
from .table import Table, _norm_type


def detect_column_types(table):
    if table._len() == 0:
        return {i: str for i in range(len(table.headers))}
    result = {}
    for col in range(len(table.headers)):
        types_seen = set()
        for row in table._row_lists():
            val = row[col] if col < len(row) else None
            if val is None or val == "":
                continue
            types_seen.add(_guess_type(val))
        if not types_seen:
            result[col] = str
        elif len(types_seen) == 1:
            result[col] = types_seen.pop()
        elif types_seen <= {int, float}:
            result[col] = float
        else:
            result[col] = str
    return result


def _guess_type(val):
    if isinstance(val, bool) and not isinstance(val, int):
        return bool
    if isinstance(val, int) and not isinstance(val, bool):
        return int
    if isinstance(val, float):
        return float
    if isinstance(val, datetime):
        return datetime
    if isinstance(val, bool):
        return bool
    s = str(val).strip()
    if s == "":
        return str
    if s.lower() in ("true", "false", "да", "нет", "yes", "no", "1", "0"):
        return bool
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y"):
        try:
            datetime.strptime(s, fmt)
            return datetime
        except ValueError:
            pass
    try:
        if "." in s or "e" in s.lower():
            float(s)
            return float
        int(s)
        return int
    except ValueError:
        pass
    return str


def apply_detected_types(table, detected=None):
    detected = detected or detect_column_types(table)
    for col, tp in detected.items():
        table._types[col] = tp
        for row in table._row_lists():
            if col < len(row) and row[col] is not None and row[col] != "":
                row[col] = table._convert(row[col], col)
    return table
