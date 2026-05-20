import copy

from .exceptions import ColumnError, RowError, TableTypeError, TableValueError
from .table import Table, _norm_type


def get_rows_by_number(table, start, stop=None, *, copy_table=False):
    n = table._len()
    if stop is None:
        stop = start + 1
    if start < 0:
        start = n + start
    if stop < 0:
        stop = n + stop
    if start < 0 or start >= n:
        raise RowError(f"start {start} вне диапазона")
    if stop < start or stop > n:
        raise RowError(f"stop {stop} неверный")
    indices = list(range(start, stop))
    if copy_table:
        rows = [copy.copy(table._row_lists()[i]) for i in indices]
        return Table(headers=list(table.headers), rows=rows, types=dict(table._types))
    return Table(_parent=_root(table), _indices=[_map_index(table, i) for i in indices])


def get_rows_by_index(table, *vals, copy_table=False):
    if not vals:
        raise RowError("нужен хотя бы один индекс")
    col0 = 0
    wanted = set()
    for v in vals:
        wanted.add(table._convert(v, col0))
    indices = []
    for i, row in enumerate(table._row_lists()):
        key = row[col0] if row else None
        if key in wanted:
            indices.append(_map_index(table, i))
    if not indices:
        raise RowError("строки не найдены")
    if copy_table:
        rows = [copy.copy(table._parent.rows[j] if table._parent else table.rows[j]) for j in indices]
        return Table(headers=list(table.headers), rows=rows, types=dict(table._types))
    return Table(_parent=_root(table), _indices=indices)


def get_column_types(table, by_number=True):
    out = {}
    for i, h in enumerate(table.headers):
        key = i if by_number else h
        out[key] = table._types.get(i, str)
    return out


def set_column_types(table, types_dict, by_number=True):
    if not types_dict:
        raise TableTypeError("пустой словарь типов")
    for col, tp in types_dict.items():
        if by_number:
            if not isinstance(col, int):
                raise ColumnError("ключ должен быть int")
            key = table._col_key(col)
        else:
            key = table._col_key(col)
        table._types[key] = _norm_type(tp)


def get_values(table, column=0):
    if table._len() == 0:
        raise RowError("таблица пустая")
    key = table._col_key(column)
    return [table._convert(row[key], key) if key < len(row) else None for row in table._row_lists()]


def get_value(table, column=0):
    if table._len() != 1:
        raise RowError(f"ожидалась 1 строка, есть {table._len()}")
    vals = get_values(table, column)
    return vals[0]


def set_values(table, values, column=0):
    key = table._col_key(column)
    if len(values) != table._len():
        raise RowError("длина values не совпадает с числом строк")
    for i, val in enumerate(values):
        ri = table._real_row_index(i)
        row = _root(table).rows[ri]
        while len(row) <= key:
            row.append(None)
        row[key] = table._convert(val, key) if val is not None else None


def set_value(table, value, column=0):
    if table._len() != 1:
        raise RowError(f"ожидалась 1 строка, есть {table._len()}")
    set_values(table, [value], column)


def print_table(table, file=None):
    if not table.headers:
        raise ColumnError("нет заголовков")
    rows = table._row_lists()
    widths = [len(str(h)) for h in table.headers]
    str_rows = []
    for row in rows:
        cells = []
        for i, h in enumerate(table.headers):
            v = row[i] if i < len(row) else None
            if v is None:
                s = ""
            elif isinstance(v, float):
                s = str(v)
            else:
                s = str(v)
            cells.append(s)
            widths[i] = max(widths[i], len(s))
        str_rows.append(cells)
    sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    def fmt_row(cells):
        parts = []
        for i, c in enumerate(cells):
            parts.append(" " + c.ljust(widths[i]) + " ")
        return "|" + "|".join(parts) + "|"
    lines = [sep, fmt_row(table.headers), sep]
    for cells in str_rows:
        lines.append(fmt_row(cells))
    lines.append(sep)
    text = "\n".join(lines)
    if file is None:
        print(text)
    else:
        with open(file, "w", encoding="utf-8") as f:
            f.write(text + "\n")


def concat(table1, table2):
    if table1.headers != table2.headers:
        raise ColumnError("разные заголовки")
    t = table1.copy()
    for row in table2._row_lists():
        t.rows.append(copy.copy(row))
    return t


def split(table, row_number):
    n = table._len()
    if row_number < 0 or row_number > n:
        raise RowError(f"row_number {row_number} вне диапазона")
    left = get_rows_by_number(table, 0, row_number, copy_table=True)
    right = get_rows_by_number(table, row_number, n, copy_table=True)
    return left, right


def filter_rows(table, bool_list, copy_table=False):
    if len(bool_list) != table._len():
        raise RowError("длина bool_list не совпадает с таблицей")
    indices = [_map_index(table, i) for i, b in enumerate(bool_list) if b]
    if not indices:
        raise RowError("нет строк с True")
    if copy_table:
        rows = [copy.copy(table._row_lists()[i]) for i, b in enumerate(bool_list) if b]
        return Table(headers=list(table.headers), rows=rows, types=dict(table._types))
    return Table(_parent=_root(table), _indices=indices)


def merge_tables(table1, table2, by_number=True, fill_none=True, on_conflict="left"):
    if on_conflict not in ("left", "right", "raise"):
        raise ColumnError(f"on_conflict {on_conflict!r} не поддерживается")
    headers = list(table1.headers)
    for h in table2.headers:
        if h not in headers:
            headers.append(h)
    for h in headers:
        i1 = table1.headers.index(h) if h in table1.headers else None
        i2 = table2.headers.index(h) if h in table2.headers else None
        if i1 is not None and i2 is not None:
            t1 = table1._types.get(i1, str)
            t2 = table2._types.get(i2, str)
            if t1 != t2 and on_conflict == "raise":
                raise ColumnError(f"конфликт типов столбца {h!r}")
    rows = []
    if by_number:
        n = max(table1._len(), table2._len())
        if table1._len() != table2._len() and on_conflict == "raise":
            raise RowError("разное число строк")
        for i in range(n):
            rows.append(_merge_row(table1, table2, i, i, headers, fill_none, on_conflict, by_number))
    else:
        map2 = {}
        for j, row in enumerate(table2._row_lists()):
            key = row[0] if row else None
            if key in map2 and on_conflict == "raise":
                raise RowError(f"дубликат индекса {key!r}")
            map2[key] = j
        used = set()
        for i, row1 in enumerate(table1._row_lists()):
            key = row1[0] if row1 else None
            j = map2.get(key)
            if j is not None:
                used.add(j)
                rows.append(_merge_row(table1, table2, i, j, headers, fill_none, on_conflict, by_number))
            elif fill_none:
                rows.append(_merge_row(table1, table2, i, None, headers, fill_none, on_conflict, by_number))
            elif on_conflict == "raise":
                raise RowError(f"нет пары для индекса {key!r}")
        if on_conflict == "raise":
            for j in range(table2._len()):
                if j not in used:
                    raise RowError("строка только во второй таблице")
        elif fill_none:
            for j in range(table2._len()):
                if j not in used:
                    rows.append(_merge_row(table1, table2, None, j, headers, fill_none, on_conflict, by_number))
    types = {}
    for i, h in enumerate(headers):
        if h in table1.headers:
            types[i] = table1._types.get(table1.headers.index(h), str)
        elif h in table2.headers:
            types[i] = table2._types.get(table2.headers.index(h), str)
    return Table(headers=headers, rows=rows, types=types)


def _merge_row(t1, t2, i1, i2, headers, fill_none, on_conflict, by_number):
    row = []
    for h in headers:
        v = None
        if i1 is not None and h in t1.headers:
            r1 = t1._row_lists()[i1]
            c1 = t1.headers.index(h)
            v1 = r1[c1] if c1 < len(r1) else None
        else:
            v1 = None
        if i2 is not None and h in t2.headers:
            r2 = t2._row_lists()[i2]
            c2 = t2.headers.index(h)
            v2 = r2[c2] if c2 < len(r2) else None
        else:
            v2 = None
        if v1 is not None and v2 is not None and v1 != v2 and on_conflict == "raise":
            raise TableValueError(f"конфликт значений {h!r}: {v1!r} и {v2!r}")
        if on_conflict == "left":
            v = v1 if v1 is not None else v2
        else:
            v = v2 if v2 is not None else v1
        if v is None and not fill_none and (v1 is None) != (v2 is None):
            pass
        row.append(v)
    return row


def _root(table):
    return table._parent if table._parent is not None else table


def _map_index(table, view_i):
    if table._parent is not None:
        return table._indices[view_i]
    return view_i
