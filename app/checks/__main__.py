from pathlib import Path

from geopandas import GeoDataFrame, read_parquet
from pandas import DataFrame
from tqdm import tqdm

from ..config import ADMIN_LEVEL_MAX, data_dir
from ..utils import is_iso3_allowed
from . import (
    dates,
    geometry_gaps,
    geometry_overlaps_self,
    geometry_valid,
    geometry_within_parent,
    languages,
    table_names,
    table_other,
    table_pcodes,
)


def output_table(data_dir: Path, checks: list) -> None:
    """Create CSV from registered checks."""
    output = None
    for _, results in checks:
        rows = [row for result in results for row in result]
        partial = DataFrame(rows).convert_dtypes()
        if output is None:
            output = partial
        else:
            output = output.merge(partial, on=["iso3", "version", "level"], how="outer")
    if output is not None:
        output = output.sort_values(["iso3", "version", "level"])
        output.to_parquet(data_dir / "checks.parquet", compression="zstd")
        output.to_csv(data_dir / "checks.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    """Generate datasets and create them in HDX."""
    checks = [
        (geometry_valid, []),
        (geometry_gaps, []),
        (geometry_overlaps_self, []),
        (geometry_within_parent, []),
        (table_pcodes, []),
        (table_names, []),
        (dates, []),
        (languages, []),
        (table_other, []),
    ]

    services = sorted((data_dir / "boundaries").iterdir())
    pbar = tqdm(services)
    for service in pbar:
        iso3 = service.name[7:10].upper()
        ver = [x for x in service.name if x.isdigit()]
        version = f"v{''.join(ver)}" if ver else None
        if not is_iso3_allowed(iso3):
            continue
        pbar.set_postfix_str(service.name)
        gdfs = []
        for level in range(ADMIN_LEVEL_MAX + 1):
            layer = service / f"{iso3.lower()}_admin{level}.parquet"
            gdf = read_parquet(layer) if layer.exists() else GeoDataFrame()
            gdfs.append(gdf)
        for index in range(ADMIN_LEVEL_MAX, -1, -1):
            if gdfs[index].empty:
                del gdfs[index]
            else:
                break
        for function, results in checks:
            result = function.main(iso3, version, gdfs)
            results.append(result)
    output_table(data_dir, checks)
