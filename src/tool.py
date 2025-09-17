"""显示与排版工具。

提供表格渲染函数，考虑中日韩字符宽度与多行换行显示。
"""

from collections.abc import Sequence
from db import WordTable
import unicodedata


def render_table(rows: list[WordTable]) -> str:
    """将 `WordTable` 列表渲染为等宽字符表格字符串。"""
    # Materialize rows for inspection
    rows_list = list(rows)
    if not rows_list:
        return ""

    headers = ("词语", "词义")

    # Simplified: rows are list[WordTable], headers are ("词语", "词义")
    header_names: tuple[str, ...] = tuple(str(h) for h in headers)
    num_cols = len(header_names)
    normalized: list[tuple[str, ...]] = [
        (str(obj.word), str(obj.meaning)) for obj in rows_list
    ]

    data = [header_names] + normalized
    if not data:
        return ""

    def _char_width(ch: str) -> int:
        # Treat fullwidth and wide as width 2; combining marks as 0
        if unicodedata.combining(ch):
            return 0
        eaw = unicodedata.east_asian_width(ch)
        return 2 if eaw in ("W", "F") else 1

    def _display_width(text: str) -> int:
        return sum(_char_width(ch) for ch in text)

    def _wrap_display(text: str, max_width: int) -> list[str]:
        # Wrap text by display width (counts CJK as width 2)
        if max_width <= 0:
            return [text]
        line: list[str] = []
        width = 0
        lines: list[str] = []
        for ch in text:
            w = _char_width(ch)
            if width + w > max_width and line:
                lines.append("".join(line))
                line = [ch]
                width = w
            else:
                line.append(ch)
                width += w
        if line:
            lines.append("".join(line))
        return lines or [""]

    num_cols = len(data[0])
    # Set reasonable max width per column (display width)
    # Heuristic: if 2 columns, assume [word, meaning]
    default_caps = [30] * num_cols
    if num_cols == 2:
        default_caps = [20, 80]
    col_caps = default_caps

    # Prepare wrapped body (exclude header)
    header = list(data[0])
    body = data[1:]

    # Wrap cells per column caps
    wrapped_body: list[list[list[str]]] = []
    for row in body:
        wrapped_row: list[list[str]] = []
        for i, cell in enumerate(row):
            cap = col_caps[i] if i < len(col_caps) else 30
            wrapped_row.append(_wrap_display(cell, cap))
        wrapped_body.append(wrapped_row)

    # Compute column widths from header and wrapped body
    col_widths = [0] * num_cols
    for i in range(num_cols):
        col_widths[i] = max(col_widths[i], _display_width(header[i]))
    for wrapped_row in wrapped_body:
        for i in range(num_cols):
            for piece in wrapped_row[i]:
                w = _display_width(piece)
                if w > col_widths[i]:
                    col_widths[i] = w

    # Alignment per column: left align first column (词语) and others
    col_align: list[str] = ["left"] * num_cols

    def _pad_cell(text: str, width: int, align: str) -> str:
        pad = width - _display_width(text)
        if pad <= 0:
            return text
        if align == "center":
            left = pad // 2
            right = pad - left
            return (" " * left) + text + (" " * right)
        # default: left align
        return text + (" " * pad)

    def format_row(row: Sequence[str]) -> str:
        padded_cells: list[str] = []
        for i, cell in enumerate(row):
            align = col_align[i] if i < len(col_align) else "left"
            padded_cells.append(_pad_cell(cell, col_widths[i], align))
        return "| " + " | ".join(padded_cells) + " |"

    def sep_line() -> str:
        # separator like +-----+-------+
        parts = ["-" * (w + 2) for w in col_widths]
        return "+" + "+".join(parts) + "+"

    lines: list[str] = []
    # top border
    lines.append(sep_line())
    # header
    lines.append(format_row(header))
    # header-data separator
    lines.append(sep_line())
    # data rows with separators between and wrapped lines
    for wrapped_row in wrapped_body:
        # Determine row height (max wrapped lines among columns)
        row_height = max(len(pieces) for pieces in wrapped_row) if wrapped_row else 1
        # Compute vertical top padding per column to achieve vertical centering for the first column
        top_pads: list[int] = []
        for i in range(num_cols):
            pieces = wrapped_row[i]
            if i == 0:
                top_pads.append((row_height - len(pieces)) // 2)
            else:
                top_pads.append(0)
        for line_idx in range(row_height):
            line_cells: list[str] = []
            for i in range(num_cols):
                pieces = wrapped_row[i]
                # Adjust line index by top padding
                adj_idx = line_idx - top_pads[i]
                cell_text = pieces[adj_idx] if 0 <= adj_idx < len(pieces) else ""
                line_cells.append(cell_text)
            lines.append(format_row(tuple(line_cells)))
        # row separator after each data row
        lines.append(sep_line())
    return "\n".join(lines)
