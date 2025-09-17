"""字典模块。

封装对词库的读取与写入、以及对大模型接口的调用与结果清洗。
"""

from openai import OpenAI

from db import DictDataBase, WordTable
from err import (
    DatabaseInsertError,
    ParseApiResponseError,
    RequestApiError,
    UserInterruptError,
)
from settings import Settings


class Dict:
    """提供词语的增删改查与释义生成。"""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.db = DictDataBase(self.settings.db_path)

    def _query_api(self, word: str) -> str:
        """调用大模型生成词语释义，并进行简单清洗。"""
        client = OpenAI(base_url=self.settings.base_url, api_key=self.settings.api_key)

        try:
            response = client.chat.completions.create(
                model=self.settings.model,
                messages=[
                    {"role": "system", "content": self.settings.system_prompt},
                    {"role": "user", "content": word},
                ],
                temperature=self.settings.temperature,
                stream=False,
            )
        except KeyboardInterrupt as e:
            raise UserInterruptError from e
        except Exception as e:
            raise RequestApiError(e) from e
        else:
            try:
                content = response.choices[0].message.content
                if not content:
                    raise RequestApiError(
                        f"the response content for word `{word}` is null"
                    )
            except Exception as e:
                raise ParseApiResponseError(e) from e

            # 简单清洗：去除可能出现的“释义”提示词与多余换行/空白
            cleaned = content.strip()
            for marker in ("释义：", "释义:", "定义：", "定义:"):
                if cleaned.startswith(marker):
                    cleaned = cleaned[len(marker) :].lstrip()
            if not cleaned.endswith("。"):
                cleaned += "。"
            return cleaned

    def add_word(self, word: str) -> None:
        """新增词语并自动生成释义。若已存在则抛出写入错误。"""
        if self.db.query_word(word):
            raise DatabaseInsertError(f"word '{word}' already exists")
        self.db.insert_word(word, self._query_api(word))

    def delete_word(self, word: str) -> None:
        """删除指定词语。"""
        self.db.delete_word(word)

    def update_word(self, word: str, meaning: str) -> None:
        """更新指定词语的词义。"""
        self.db.update_word(word, meaning)

    def query_word(self, word: str) -> WordTable | None:
        """查询指定词语，返回表记录或 None。"""
        return self.db.query_word(word)

    def query_random(self, count: int) -> list[WordTable]:
        """随机查询指定数量的词语。"""
        return self.db.query_random(count)

    def query_range(self, start: int, end: int) -> list[WordTable]:
        """查询指定位置范围内的词语（按 id 升序）。"""
        return self.db.query_range(start, end)

    def close_db(self) -> None:
        """关闭数据库连接。"""
        self.db.close()
