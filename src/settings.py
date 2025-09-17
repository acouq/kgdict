"""配置模块。

从环境变量加载 API Key，定义调用大模型与数据库的相关配置。
"""

import os


from err import ParseApiKeyError


class Settings:
    def __init__(self) -> None:
        # deepseek api 设置
        self.api_key = self._get_api_key()
        self.base_url = "https://api.deepseek.com"
        self.temperature = 0.2
        self.model = "deepseek-chat"
        self.system_prompt = (
            "你是词语字典，用户输入词语，你给出释义，要求返回的内容中不能有释义这两个字"
        )

        # 数据库设置
        self._db_dir = os.getenv("APPDATA") or os.path.join(
            os.path.expanduser("~"), ".kgdict"
        )
        self.db_path = os.path.join(self._db_dir, "kgdict.db")

    def _get_api_key(self) -> str:
        """从环境变量读取 API Key，若缺失则抛出 `ParseApiKeyError`。"""
        api_key = (
            os.getenv("DEEPSEEK_API_KEY")
            or os.getenv("OPENAI_API_KEY")
            or os.getenv("API_KEY")
        )

        if not api_key:
            raise ParseApiKeyError(
                "api key not found, please set environment variable DEEPSEEK_API_KEY or OPENAI_API_KEY"
            )

        return api_key
