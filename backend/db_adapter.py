import re
import urllib.parse
from typing import Any, List, Dict, Optional

class PostgresRow(dict):
    """Row object that supports both dict indexing (row['col']) and integer indexing (row[0])."""
    def __init__(self, cursor_description, row_tuple):
        super().__init__()
        self._list = list(row_tuple) if row_tuple is not None else []
        if cursor_description and row_tuple:
            for i, col in enumerate(cursor_description):
                col_name = col.name if hasattr(col, "name") else col[0]
                self[col_name] = row_tuple[i]

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._list[key]
        return super().__getitem__(key)

    def get(self, key, default=None):
        if isinstance(key, int):
            return self._list[key] if 0 <= key < len(self._list) else default
        return super().get(key, default)

class PostgresCursorWrapper:
    """Wraps a psycopg2/pg8000 cursor to provide sqlite3-compatible interface."""
    def __init__(self, raw_cursor):
        self._cursor = raw_cursor
        self.lastrowid = None

    def _convert_query(self, sql: str) -> str:
        s = sql.strip()

        # Convert SQLite VN_LOWER to standard PostgreSQL LOWER
        s = re.sub(r'\bVN_LOWER\(', 'LOWER(', s, flags=re.IGNORECASE)

        # Convert SQLite INSERT OR IGNORE INTO to PostgreSQL ON CONFLICT DO NOTHING
        if re.search(r'\bINSERT\s+OR\s+IGNORE\s+INTO\b', s, flags=re.IGNORECASE):
            s = re.sub(r'\bINSERT\s+OR\s+IGNORE\s+INTO\b', 'INSERT INTO', s, flags=re.IGNORECASE)
            if 'ON CONFLICT' not in s.upper():
                s = s.rstrip(';') + ' ON CONFLICT DO NOTHING'

        # Convert parameter placeholders from ? to %s
        s = s.replace('?', '%s')
        return s

    def execute(self, sql: str, params: Any = None):
        converted_sql = self._convert_query(sql)

        # Handle lastrowid for INSERT statements if needed
        is_insert = converted_sql.strip().upper().startswith("INSERT INTO")
        has_returning = "RETURNING" in converted_sql.upper()

        if is_insert and not has_returning and "ON CONFLICT DO NOTHING" not in converted_sql.upper():
            # Append RETURNING id so we can capture lastrowid
            converted_sql = converted_sql.rstrip(";") + " RETURNING id;"

        if params is not None:
            if isinstance(params, (list, tuple)):
                self._cursor.execute(converted_sql, tuple(params))
            elif isinstance(params, dict):
                self._cursor.execute(converted_sql, params)
            else:
                self._cursor.execute(converted_sql, (params,))
        else:
            self._cursor.execute(converted_sql)

        # If we appended RETURNING id or it has returning
        if is_insert and ("RETURNING" in converted_sql.upper()):
            try:
                row = self._cursor.fetchone()
                if row:
                    self.lastrowid = row[0]
            except Exception:
                pass
        return self

    def executemany(self, sql: str, seq_of_params: List[Any]):
        converted_sql = self._convert_query(sql)
        return self._cursor.executemany(converted_sql, seq_of_params)

    def fetchone(self) -> Optional[PostgresRow]:
        row = self._cursor.fetchone()
        if row is None:
            return None
        return PostgresRow(self._cursor.description, row)

    def fetchall(self) -> List[PostgresRow]:
        rows = self._cursor.fetchall()
        if not rows:
            return []
        return [PostgresRow(self._cursor.description, r) for r in rows]

    def close(self):
        try:
            self._cursor.close()
        except Exception:
            pass

    def __iter__(self):
        for row in self.fetchall():
            yield row

class PostgresConnectionWrapper:
    """Wraps a psycopg2/pg8000 connection to provide sqlite3-compatible interface."""
    def __init__(self, raw_conn):
        self._conn = raw_conn

    def cursor(self):
        return PostgresCursorWrapper(self._conn.cursor())

    def execute(self, sql: str, params: Any = None):
        c = self.cursor()
        c.execute(sql, params)
        return c

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass

    def create_function(self, name, num_args, func):
        # No-op in PostgreSQL since native functions are used
        pass

def connect_postgres(db_url: str) -> PostgresConnectionWrapper:
    """Establish a connection to PostgreSQL (Supabase) using psycopg2 or pg8000."""
    url = db_url.strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]

    try:
        import psycopg2
        raw_conn = psycopg2.connect(url, connect_timeout=10)
        raw_conn.autocommit = False
        return PostgresConnectionWrapper(raw_conn)
    except ImportError:
        pass

    try:
        import pg8000.dbapi
        # Parse connection string for pg8000
        parsed = urllib.parse.urlparse(url)
        raw_conn = pg8000.dbapi.connect(
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip("/"),
            timeout=10
        )
        raw_conn.autocommit = False
        return PostgresConnectionWrapper(raw_conn)
    except Exception as e:
        raise RuntimeError(f"Không thể kết nối đến PostgreSQL Supabase: {e}")
