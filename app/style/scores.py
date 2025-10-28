from xlsxwriter import Workbook
from xlsxwriter.format import Format
from xlsxwriter.worksheet import Worksheet

FormatConf = dict[str, str | float | Format]


def format_between(cell_format: Format, min_val: float, max_val: float) -> FormatConf:
    """Get a configuration used for conditional formatting between values in Excel."""
    return {
        "type": "cell",
        "criteria": "between",
        "minimum": min_val,
        "maximum": max_val,
        "format": cell_format,
    }


def score_style(last_row: int, last_col: int, book: Workbook, sheet: Worksheet) -> None:
    """Apply red / orange / yellow styling to excel values falling between value ranges.

    The first few columns of the output include location names and iso3 codes.
    - first_col: zero-index location where decimal data begins.

    - Decimals are formatted as percentages.
    - Red formatting is applied for values: 0-33%
    - Orange formatting is applied for values: 33-67%
    - Yellow formatting is applied for values: 67-100%
    """
    first_row = 1
    first_col = 3
    format_percent = book.add_format({"num_format": "0%"})
    format_rd = book.add_format({"bg_color": "#FFC7CE", "font_color": "#9C0006"})
    format_or = book.add_format({"bg_color": "#FFCC99", "font_color": "#3F3F76"})
    format_yl = book.add_format({"bg_color": "#FFEB9C", "font_color": "#9C6500"})
    between_rd = format_between(format_rd, 0, 0.333)
    between_or = format_between(format_or, 0.333, 0.667)
    between_yl = format_between(format_yl, 0.667, 0.999)
    sheet.set_column(first_col, last_col, None, format_percent)
    sheet.conditional_format(first_row, first_col, last_row, last_col, between_rd)
    sheet.conditional_format(first_row, first_col, last_row, last_col, between_or)
    sheet.conditional_format(first_row, first_col, last_row, last_col, between_yl)
    sheet.autofit()
