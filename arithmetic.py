from .exceptions import TableTypeError, TableValueError
from .operations import set_column_types, set_values

_NUM = (int, float, bool)


def _check_numeric(table, key):
    tp = table._types.get(key, str)
    if tp not in _NUM:
        raise TableTypeError(f"столбец {key} не числовой")


def _arith(table, col_a, col_b, op, result_col=None):
    ka = table._col_key(col_a)
    kb = table._col_key(col_b)
    _check_numeric(table, ka)
    _check_numeric(table, kb)
    out = []
    for row in table._row_lists():
        a = row[ka] if ka < len(row) else None
        b = row[kb] if kb < len(row) else None
        if a is None or b is None:
            out.append(None)
            continue
        if op == "add":
            out.append(a + b)
        elif op == "sub":
            out.append(a - b)
        elif op == "mul":
            out.append(a * b)
        else:
            if b == 0:
                raise TableValueError("деление на ноль")
            out.append(a / b)
    if result_col is None:
        syms = {"add": "+", "sub": "-", "mul": "*", "div": "/"}
        sym = syms[op]
        result_col = f"{table.headers[ka]}{sym}{table.headers[kb]}"
    if result_col not in table.headers:
        table.headers.append(result_col)
        rk = len(table.headers) - 1
        table._types[rk] = float
        for row in table._row_lists():
            while len(row) <= rk:
                row.append(None)
    set_values(table, out, result_col)
    set_column_types(table, {table._col_key(result_col): float}, by_number=True)
    return table


def add(table, col_a, col_b, result_col=None):
    return _arith(table, col_a, col_b, "add", result_col)


def sub(table, col_a, col_b, result_col=None):
    return _arith(table, col_a, col_b, "sub", result_col)


def mul(table, col_a, col_b, result_col=None):
    return _arith(table, col_a, col_b, "mul", result_col)


def div(table, col_a, col_b, result_col=None):
    return _arith(table, col_a, col_b, "div", result_col)


def _cmp(table, col_a, col_b, op):
    ka = table._col_key(col_a)
    kb = table._col_key(col_b)
    out = []
    for row in table._row_lists():
        a = row[ka] if ka < len(row) else None
        b = row[kb] if kb < len(row) else None
        if a is None or b is None:
            out.append(False)
            continue
        try:
            a = table._convert(a, ka)
            b = table._convert(b, kb)
        except Exception:
            out.append(False)
            continue
        if op == "eq":
            out.append(a == b)
        elif op == "ne":
            out.append(a != b)
        elif op == "gr":
            out.append(a > b)
        elif op == "ls":
            out.append(a < b)
        elif op == "ge":
            out.append(a >= b)
        else:
            out.append(a <= b)
    return out


def eq(table, col_a, col_b):
    return _cmp(table, col_a, col_b, "eq")


def ne(table, col_a, col_b):
    return _cmp(table, col_a, col_b, "ne")


def gr(table, col_a, col_b):
    return _cmp(table, col_a, col_b, "gr")


def ls(table, col_a, col_b):
    return _cmp(table, col_a, col_b, "ls")


def ge(table, col_a, col_b):
    return _cmp(table, col_a, col_b, "ge")


def le(table, col_a, col_b):
    return _cmp(table, col_a, col_b, "le")
