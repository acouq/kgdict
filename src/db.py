"""数据库访问层 (SQLite)。

定义表模型与对词库的增删改查操作，所有异常统一封装为自定义数据库错误类型。
"""

import sqlite3
from pathlib import Path

from err import (
    DatabaseError,
    DatabaseInsertError,
    DatabaseDeleteError,
    DatabaseQueryError,
    DatabaseUpdateError,
)


class WordTable:
    """词表行模型。"""

    def __init__(self, word: str, meaning: str) -> None:
        self.word = word
        self.meaning = meaning


class DictDataBase:
    """词典数据库封装，负责连接、建表与 CRUD。"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._connect()
        self._create_table()

    def _connect(self) -> None:
        """建立到 SQLite 的连接并启用 `Row` 工厂。"""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        except Exception as e:
            raise DatabaseError(e) from e

    def _create_table(self) -> None:
        """创建表和触发器（若不存在）。"""
        try:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS words (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  word TEXT NOT NULL UNIQUE,
                  meaning TEXT NOT NULL DEFAULT '',
                  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            self.conn.execute(
                """
                CREATE TRIGGER IF NOT EXISTS trg_words_updated
                AFTER UPDATE ON words
                FOR EACH ROW WHEN NEW.updated_at = OLD.updated_at BEGIN
                  UPDATE words SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END;
                """
            )
            self.conn.commit()
        except Exception as e:
            raise DatabaseError(e) from e

    def close(self) -> None:
        """关闭数据库连接。"""
        try:
            self.conn.close()
        except Exception as e:
            raise DatabaseError(e) from e

    # def upsert_word(self, word: str, meaning: str) -> None:
    #     try:
    #         self.conn.execute(
    #             """
    #             INSERT INTO words(word, meaning)
    #             VALUES(?, ?)
    #             ON CONFLICT(word) DO UPDATE SET meaning=excluded.meaning;
    #             """,
    #             (word, meaning),
    #         )
    #         self.conn.commit()
    #     except Exception as e:
    #         # upsert 统一视为写入错误
    #         raise DatabaseInsertError(str(e))

    def insert_word(self, word: str, meaning: str) -> None:
        """插入新词。若违反唯一约束或其他错误，抛出 `DatabaseInsertError`。"""
        try:
            self.conn.execute(
                """
                INSERT INTO words(word, meaning)
                VALUES(?, ?);
                """,
                (word, meaning),
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            raise DatabaseInsertError(
                f"word '{word}' already exists or violates constraints"
            )
        except Exception as e:
            raise DatabaseInsertError(e) from e

    def delete_word(self, word: str) -> None:
        """删除指定词语，若不存在则抛出 `DatabaseDeleteError`。"""
        try:
            cur = self.conn.execute("DELETE FROM words WHERE word = ?", (word,))
            if cur.rowcount == 0:
                raise DatabaseDeleteError(f"word '{word}' not found in database")
            self.conn.commit()
        except DatabaseDeleteError:
            raise
        except Exception as e:
            raise DatabaseDeleteError(e) from e

    def update_word(self, word: str, meaning: str) -> None:
        """更新词义，若目标不存在或约束失败则抛错。"""
        try:
            cur = self.conn.execute(
                "UPDATE words SET meaning = ? WHERE word = ?",
                (meaning, word),
            )
            if cur.rowcount == 0:
                raise DatabaseUpdateError(f"word '{word}' not found in database")
            self.conn.commit()
        except DatabaseUpdateError:
            raise
        except sqlite3.IntegrityError as e:
            raise DatabaseUpdateError(e) from e
        except Exception as e:
            raise DatabaseUpdateError(e) from e

    def query_word(self, word: str) -> WordTable | None:
        """按词语精确查询，返回 `WordTable` 或 `None`。"""
        try:
            cur = self.conn.execute("SELECT * FROM words WHERE word = ?", (word,))
            row = cur.fetchone()
            return WordTable(row["word"], row["meaning"]) if row else None
        except Exception as e:
            raise DatabaseQueryError(e) from e

    def query_random(self, count: int) -> list[WordTable]:
        """随机返回指定数量的词条。"""
        try:
            cur = self.conn.execute(
                "SELECT * FROM words ORDER BY RANDOM() LIMIT ?", (count,)
            )
            return [WordTable(row["word"], row["meaning"]) for row in cur.fetchall()]
        except Exception as e:
            raise DatabaseQueryError(e) from e

    def query_range(self, start: int, end: int) -> list[WordTable]:
        """按 id 升序返回闭区间 [start, end] 的词条。"""
        try:
            offset = max(0, start - 1)
            limit = max(0, end - start + 1)
            cur = self.conn.execute(
                "SELECT * FROM words ORDER BY id ASC LIMIT ? OFFSET ?",
                (limit, offset),
            )
            return [WordTable(row["word"], row["meaning"]) for row in cur.fetchall()]
        except Exception as e:
            raise DatabaseQueryError(e) from e
