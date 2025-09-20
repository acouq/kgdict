"""命令行解析模块。

提供命令定义与参数校验，将解析结果封装为 `UserInput` 供上层使用。

命令概览：
- add: 增加一个或多个词语
- del: 删除一个或多个词语
- set: 修改指定词语的词义
- get: 查询一个或多个词语
- pick: 随机抽取 N 个词语
- range: 按位置范围查询词语
"""

import argparse
from typing import Any, NoReturn

from err import ParseUserInputError
from user_input import UserInput


_VERSION = "0.1.3"


class QuietArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        raise argparse.ArgumentError(None, message)


def _positive_int(text: str) -> int:
    """将文本解析为正整数，失败时抛出参数错误。"""
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("must be integer") from None
    if value <= 0:
        raise argparse.ArgumentTypeError("must be positive integer") from None
    return value


def _non_empty(text: str) -> str:
    """裁剪并校验非空字符串。"""
    value = text.strip()
    if value == "":
        raise argparse.ArgumentTypeError("must be non-empty str")
    return value


def _build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = QuietArgumentParser(
        prog="kgdict",
        description=f"考公词语字典 v{_VERSION}",
        exit_on_error=False,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s v{_VERSION}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="增加: 词语...")
    p_add.add_argument("words", nargs="+", type=_non_empty)

    p_del = sub.add_parser("del", help="删除: 词语...")
    p_del.add_argument("words", nargs="+", type=_non_empty)

    p_set = sub.add_parser("set", help="修改: 词语 词义")
    p_set.add_argument("word", type=_non_empty)
    p_set.add_argument("meaning", type=_non_empty)

    p_qw = sub.add_parser("get", help="查询: 词语...")
    p_qw.add_argument("words", nargs="+", type=_non_empty)

    p_qn = sub.add_parser("pick", help="查询: 随机抽取 N 个词语")
    p_qn.add_argument("n", type=_positive_int)

    p_r = sub.add_parser("range", help="阅读: N1 N2, 查询第 N1 个到第 N2 个之间的词语")
    p_r.add_argument("n1", type=_positive_int)
    p_r.add_argument("n2", type=_positive_int)

    return parser


def get_user_input(argv: Any | None = None) -> UserInput:
    """解析参数并返回 `UserInput`。

    - 当解析失败时，转换为 `ParseUserInputError` 以统一错误输出。
    """
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except argparse.ArgumentError as e:
        raise ParseUserInputError(f"{e}\n\n{parser.format_help()}") from e
    else:
        return UserInput(args.command, vars(args))
