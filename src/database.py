import sqlite3
from contextlib import closing
from typing import Any

from src.definitions import APP_DIR
from src.parser import warn

DB_PATH = APP_DIR / "db" / "leaderboard.db"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS highscore(
    name TEXT NOT NULL,
    score INTEGER
)
"""


class Database:
    def __init__(self) -> None:
        self._warned: set[str] = set()

    def _warn_once(self, message: str) -> None:
        if message not in self._warned:
            self._warned.add(message)
            warn(message)

    def initialize_database(self) -> None:
        """
        Create the database folder and the highscore table [name, score]
        """
        try:
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            with closing(sqlite3.connect(DB_PATH)) as con:
                con.execute(CREATE_TABLE)
        except (sqlite3.Error, OSError) as e:
            self._warn_once(
                f"cannot open the highscore database {DB_PATH}: {e}"
            )

    def _execute(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        """
        Execute a query that changes the database and return the amount of
        rows changed, or 0 if the database could not be written
        """
        try:
            with closing(sqlite3.connect(DB_PATH)) as con:
                cur = con.execute(sql, params)
                con.commit()
                return cur.rowcount
        except sqlite3.Error as e:
            self._warn_once(f"cannot save the highscore: {e}")
            return 0

    def _fetch_all(
        self, sql: str, params: tuple[Any, ...] = ()
    ) -> list[tuple[Any, ...]]:
        """
        Return all the rows of a query, or an empty list if the database
        could not be read
        """
        try:
            with closing(sqlite3.connect(DB_PATH)) as con:
                return con.execute(sql, params).fetchall()
        except sqlite3.Error as e:
            self._warn_once(f"cannot read the highscores: {e}")
            return []

    def check_score_player(self, name: str) -> list[tuple[int]]:
        """
        Return the saved score of a player, empty if the name is new
        """
        return self._fetch_all(
            "SELECT score FROM highscore WHERE name = ?", (name,)
        )

    def insert_player(self, name: str, score: int) -> int:
        """
        Insert a player in a database
        """
        return self._execute(
            """
        INSERT INTO highscore(name, score)
        VALUES (?, ?);
        """,
            (name, score),
        )

    def update_score(self, name: str, new_score: int) -> int:
        """
        Update the score of a player that
        is already in the database
        """
        return self._execute(
            """
        UPDATE highscore
        SET score = ?
        WHERE name = ?;
        """,
            (new_score, name),
        )

    def top_scores(self, limit: int = 10) -> list[tuple[str, int]]:
        """
        Return the best 'limit' (name, score) pairs, highest score first
        """
        return self._fetch_all(
            """
        SELECT name, score FROM highscore ORDER BY score DESC LIMIT ?
        """,
            (limit,),
        )
