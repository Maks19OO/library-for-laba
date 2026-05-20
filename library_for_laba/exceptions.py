class TableError(Exception):
    pass


class ColumnError(TableError):
    pass


class RowError(TableError):
    pass


class TableTypeError(TableError):
    pass


class TableValueError(TableError):
    pass


class FileError(TableError):
    pass


class MergeError(TableError):
    pass
