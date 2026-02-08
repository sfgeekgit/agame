from django.db import connection


def _execute(sql, params=(), *, fetch=None, dicts=False):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        if fetch == 'one':
            row = cursor.fetchone()
            if dicts and row is not None:
                return _row_to_dict(cursor, row)
            return row
        if fetch == 'all':
            rows = cursor.fetchall()
            if dicts:
                return _rows_to_dicts(cursor, rows)
            return rows
        return cursor.rowcount


def sql(sql, params=(), *, fetch=None):
    return _execute(sql, params, fetch=fetch, dicts=False)


def fetch_one(sql, params=()):
    return _execute(sql, params, fetch='one', dicts=False)


def fetch_all(sql, params=()):
    return _execute(sql, params, fetch='all', dicts=False)


def fetch_dicts(sql, params=()):
    return _execute(sql, params, fetch='all', dicts=True)


def execute(sql, params=()):
    return _execute(sql, params, fetch=None, dicts=False)


def _row_to_dict(cursor, row):
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


def _rows_to_dicts(cursor, rows):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in rows]
