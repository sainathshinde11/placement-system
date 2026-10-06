"""Thin database layer. Swap the connector here to move to Oracle (oracledb)."""
from contextlib import contextmanager
import mysql.connector
from config import DB_CONFIG


class Database:
    def __init__(self, config=None):
        self._conn = mysql.connector.connect(**(config or DB_CONFIG))

    def fetch_all(self, query, params=()):
        cur = self._conn.cursor(dictionary=True)
        try:
            cur.execute(query, params)
            return cur.fetchall()
        finally:
            cur.close()

    def fetch_one(self, query, params=()):
        rows = self.fetch_all(query, params)
        return rows[0] if rows else None

    def execute(self, query, params=()):
        """Single write, auto-commit. Returns lastrowid."""
        cur = self._conn.cursor()
        try:
            cur.execute(query, params)
            self._conn.commit()
            return cur.lastrowid
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cur.close()

    @contextmanager
    def transaction(self):
        """Multi-statement atomic block: with db.transaction() as cur: ..."""
        cur = self._conn.cursor(dictionary=True)
        try:
            yield cur
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
        finally:
            cur.close()

    def close(self):
        self._conn.close()