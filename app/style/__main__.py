from pandas import DataFrame, ExcelWriter, Timestamp, read_parquet
from xlsxwriter import Workbook

from ..config import data_dir
from .scores import score_style


def main() -> None:
    """Aggregate scores and outputs to an Excel workbook with red/amber/green coloring.

    1. Groups and averages the scores generated in this module and outputs as a CSV.
    2. Applied styling to the dataset generated in step 1 and saves as Excel.
    3. Adds all CSVs generated in previous modules to the Excel workbook.
    4. Adds a final sheet specifying which date the workbook was generated on.
    """
    with ExcelWriter(data_dir / "cod_ab.xlsx") as writer:
        scores = read_parquet(data_dir / "scores.parquet")
        scores.to_excel(writer, sheet_name="scores", index=False)
        if isinstance(writer.book, Workbook):
            score_style(
                len(scores.index),
                len(scores.columns) - 1,
                writer.book,
                writer.sheets["scores"],
            )
        for sheet in ["checks", "metadata", "updated"]:
            df1 = read_parquet(data_dir / f"{sheet}.parquet")
            df1.to_excel(writer, sheet_name=sheet, index=False)
            writer.sheets[sheet].autofit()
        df_date = DataFrame([{"date": Timestamp.now().date()}])
        df_date.to_parquet(data_dir / "date.parquet", compression="zstd")
        df_date.to_csv(data_dir / "date.csv", index=False, encoding="utf-8-sig")
        df_date.to_excel(writer, sheet_name="date", index=False)
        writer.sheets["date"].autofit()
