import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "db" / "leaderboard.db"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS highscore(
    name TEXT NOT NULL,
    score INTEGER
)
"""


class Database:
    def initialize_database(self) -> None:
        """
        Create the database with initial table highscore [name, score]
        """
        with closing(sqlite3.connect(DB_PATH)) as con:
            con.execute(CREATE_TABLE)

    def execute(self, sql: str, params: tuple = ()) -> int:
        """
        Execute an certain query and return the amount
        of rows that has been changed
        """
        with closing(sqlite3.connect(DB_PATH)) as con:
            cur = con.execute(sql, params)
            return cur.rowcount

    def fetch_all(self, sql: str, params: tuple = ()) -> list[tuple]:
        """
        Return all the currencies for a certain query
        """
        with closing(sqlite3.connect(DB_PATH)) as con:
            return con.execute(sql, params).fetchall()

    def check_name(self, name: str) -> list[tuple]:
        """
        Check if a name already exists in a database
        """
        return self.fetch_all(f"SELECT * FROM highscore WHERE name = '{name}'")

    def insert_player(self, name: str, score: int) -> int:
        """
        Insert a player in a database
        """
        return self.execute(f"""
        INSERT INTO highscore(name, score)
        VALUES ('{name}', {score});
        """)

    def update_score(self, name: str, new_score: int) -> int:
        """
        Update the score of a player that
        is already in the database
        """
        return self.execute(f"""
        UPDATE highscore
        SET score = {new_score}
        WHERE name = '{name}';
        """)
