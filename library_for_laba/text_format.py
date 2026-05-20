import os

from .exceptions import FileError
from .operations import print_table


def save_table(path, table):
    if not path:
        raise FileError("не указан путь")
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        raise FileError(f"папка не существует: {d}")
    print_table(table, file=path)
    return path
