"""用户输入数据模型。

该模块将解析后的命令行参数映射为结构化的数据类，便于上层业务逻辑使用。
"""

from dataclasses import dataclass


@dataclass
class AddArgs:
    """add 命令参数。

    - words: 待新增的词语列表
    """

    words: list[str]


@dataclass
class DelArgs:
    """del 命令参数：待删除的词语列表。"""

    words: list[str]


@dataclass
class SetArgs:
    """set 命令参数：设置单个词语的词义。"""

    word: str
    meaning: str


@dataclass
class GetArgs:
    """get 命令参数：待查询的词语列表。"""

    words: list[str]


@dataclass
class PickArgs:
    """pick 命令参数：随机抽取的数量。"""

    count: int


@dataclass
class RangeArgs:
    """range 命令参数：基于位置区间的开始与结束（闭区间）。"""

    start: int
    end: int


class UserInput:
    """封装一次命令行操作及其参数。"""

    def __init__(self, op: str, kwargs: dict[str, object]) -> None:
        match op:
            case "add":
                self.add = AddArgs(kwargs.get("words"))
            case "del":
                self.delete = DelArgs(kwargs.get("words"))
            case "set":
                self.set = SetArgs(kwargs.get("word"), kwargs.get("meaning"))
            case "get":
                self.get = GetArgs(kwargs.get("words"))
            case "pick":
                self.pick = PickArgs(kwargs.get("n"))
            case "range":
                start, end = (
                    min(kwargs.get("n1"), kwargs.get("n2")),
                    max(kwargs.get("n1"), kwargs.get("n2")),
                )
                self.range = RangeArgs(start, end)
        self.op = op
