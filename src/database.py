import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "leaderboard.db"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS highscore(
    name TEXT NOT NULL,
    score INTEGER
)
"""

SQL = """
SELECT * from sqlite_master
"""


class Database:
    def __init__(self) -> None:
        pass

    def initialize_database(self) -> None:
        """
        Create the database with initial table highscore [name, score]
        """
        with sqlite3.connect(DB_PATH) as con:
            con.execute(CREATE_TABLE)

    def execute(self, sql: str, params: tuple = ()) -> int:
        """
        Execute an certain query and return the amount
        of rows that has been changed
        """
        with sqlite3.connect(DB_PATH) as con:
            cur = con.execute(sql, params)
            return cur.rowcount

    def fetch_all(self, sql: str, params: tuple = ()) -> list[tuple]:
        """
        Return all the currencies for a certain query
        """
        with sqlite3.connect(DB_PATH) as con:
            return con.execute(sql, params).fetchall()

    def check_name(self, name: str) -> None:
        self.fetch_all(f"SELECT * FROM highscore WHERE name = '{name}'")
