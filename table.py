import copy
from datetime import datetime

from .exceptions import ColumnError, RowError, TableTypeError, TableValueError


TYPES = {
    int: int,
    float: float,
    bool: bool,
    str: str,
    datetime: datetime,
}


def _norm_type(t):
    if t is None:
        return str
    if isinstance(t, str):
        m = {
            "int": int,
            "float": float,
            "bool": bool,
            "str": str,
            "datetime": datetime,
        }
        if t not in m:
            raise TableTypeError(f"неизвестный тип: {t}")
        return m[t]
    if t not in TYPES:
        raise TableTypeError(f"неизвестный тип: {t}")
    return t


class Table:
    def __init__(self, headers=None, rows=None, types=None, _parent=None, _indices=None):
        if _parent is not None:
            self._parent = _parent
            self._indices = list(_indices) if _indices is not None else []
            self.headers = _parent.headers
            self._types = _parent._types
            return
        self._parent = None
        self._indices = None
        self.headers = list(headers) if headers else []
        self.rows = [list(r) for r in rows] if rows else []
        self._types = {}
        if types:
            for k, v in types.items():
                self._types[self._col_key(k)] = _norm_type(v)
        for i in range(len(self.headers)):
            if i not in self._types:
                self._types[i] = str

    def _col_key(self, column):
        if isinstance(column, int):
            if column < 0 or column >= len(self.headers):
                raise ColumnError(f"столбец {column} не существует")
            return column
        if column not in self.headers:
            raise ColumnError(f"столбец {column!r} не существует")
        return self.headers.index(column)

    def _row_lists(self):
        if self._parent is not None:
            return [self._parent.rows[i] for i in self._indices]
        return self.rows

    def _len(self):
        if self._parent is not None:
            return len(self._indices)
        return len(self.rows)

    def _real_row_index(self, view_row):
        if self._parent is not None:
            if view_row < 0 or view_row >= len(self._indices):
                raise RowError(f"строка {view_row} не существует")
            return self._indices[view_row]
        if view_row < 0 or view_row >= len(self.rows):
            raise RowError(f"строка {view_row} не существует")
        return view_row

    def _convert(self, value, col_key):
        if value is None or value == "":
            return None
        tp = self._types.get(col_key, str)
        if tp is bool:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                s = value.strip().lower()
                if s in ("true", "1", "да", "yes"):
                    return True
                if s in ("false", "0", "нет", "no"):
                    return False
            raise TableValueError(f"не bool: {value!r}")
        if tp is datetime:
            if isinstance(value, datetime):
                return value
            if isinstance(value, str):
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M:%S", "%d.%m.%Y"):
                    try:
                        return datetime.strptime(value.strip(), fmt)
                    except ValueError:
                        pass
            raise TableValueError(f"не дата: {value!r}")
        try:
            return tp(value)
        except (ValueError, TypeError) as e:
            raise TableValueError(f"не {tp.__name__}: {value!r}") from e

    def copy(self):
        return Table(
            headers=list(self.headers),
            rows=copy.deepcopy(self._row_lists()),
            types={k: v for k, v in self._types.items()},
        )

    def to_dict(self):
        return {
            "headers": list(self.headers),
            "rows": copy.deepcopy(self._row_lists()),
            "types": {k: v for k, v in self._types.items()},
        }

    @classmethod
    def from_dict(cls, d):
        t = cls(headers=d.get("headers", []), rows=d.get("rows", []))
        types = d.get("types", {})
        for k, v in types.items():
            ki = int(k) if isinstance(k, str) and str(k).isdigit() else k
            t._types[ki] = v if isinstance(v, type) else _norm_type(v)
        return t

    def print_table(self, file=None):
        from .operations import print_table
        print_table(self, file=file)

    def get_rows_by_number(self, start, stop=None, copy_table=False):
        from .operations import get_rows_by_number
        return get_rows_by_number(self, start, stop, copy_table=copy_table)

    def get_rows_by_index(self, *vals, copy_table=False):
        from .operations import get_rows_by_index
        return get_rows_by_index(self, *vals, copy_table=copy_table)

    def get_column_types(self, by_number=True):
        from .operations import get_column_types
        return get_column_types(self, by_number=by_number)

    def set_column_types(self, types_dict, by_number=True):
        from .operations import set_column_types
        return set_column_types(self, types_dict, by_number=by_number)

    def get_values(self, column=0):
        from .operations import get_values
        return get_values(self, column=column)

    def get_value(self, column=0):
        from .operations import get_value
        return get_value(self, column=column)

    def set_values(self, values, column=0):
        from .operations import set_values
        return set_values(self, values, column=column)

    def set_value(self, value, column=0):
        from .operations import set_value
        return set_value(self, value, column=column)
