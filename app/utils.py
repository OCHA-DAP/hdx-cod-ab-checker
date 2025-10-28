import logging
from pathlib import Path
from subprocess import run
from typing import Literal

from httpx import Client, Response
from tenacity import retry, stop_after_attempt, wait_fixed

from .config import (
    ARCGIS_PASSWORD,
    ARCGIS_SERVER,
    ARCGIS_SERVICE_URL,
    ARCGIS_USERNAME,
    ATTEMPT,
    EXPIRATION,
    ISO3_EXCLUDE,
    ISO3_INCLUDE,
    TIMEOUT,
    WAIT,
)

logger = logging.getLogger(__name__)
cwd = Path(__file__).parent


@retry(stop=stop_after_attempt(ATTEMPT), wait=wait_fixed(WAIT))
def client_get(url: str, params: dict | None = None) -> Response:
    """HTTP GET with retries, waiting, and longer timeouts."""
    with Client(http2=True, timeout=TIMEOUT) as client:
        return client.get(url, params=params)


def generate_token() -> str:
    """Generate a token for ArcGIS Server."""
    url = f"{ARCGIS_SERVER}/portal/sharing/rest/generateToken"
    data = {
        "username": ARCGIS_USERNAME,
        "password": ARCGIS_PASSWORD,
        "referer": f"{ARCGIS_SERVER}/portal",
        "expiration": EXPIRATION,
        "f": "json",
    }
    with Client(http2=True) as client:
        r = client.post(url, data=data).json()
        return r["token"]


def get_feature_server_url(iso3: str) -> str:
    """Get a url for a feature server."""
    return f"{ARCGIS_SERVICE_URL}/cod_ab_{iso3.lower()}/FeatureServer"


def get_epsg_ease(min_lat: float, max_lat: float) -> Literal[6931, 6932, 6933]:
    """Get the code for appropriate Equal-Area Scalable Earth grid based on latitude.

    Args:
        min_lat: Minimum latitude of geometry from bounds.
        max_lat: Maximum latitude of geometry from bounds.

    Returns:
        EPSG for global EASE grid if area touches neither or both poles, otherwise a
        north or south grid if the area touches either of those zones.

    """
    latitude_poles = 80
    latitude_equator = 0
    epsg_ease_north = 6931
    epsg_ease_south = 6932
    epsg_ease_global = 6933
    if max_lat >= latitude_poles and min_lat >= latitude_equator:
        return epsg_ease_north
    if min_lat <= -latitude_poles and max_lat <= latitude_equator:
        return epsg_ease_south
    return epsg_ease_global


def is_empty(string: str) -> bool:
    """Check if string is empty."""
    return str(string).strip() == ""


def is_iso3_allowed(iso3: str) -> bool:
    """Check if iso3 value is in the allowed list."""
    iso3_include = [x.strip() for x in ISO3_INCLUDE.split(",") if x.strip() != ""]
    iso3_exclude = [x.strip() for x in ISO3_EXCLUDE.split(",") if x.strip() != ""]
    return not (
        (iso3_include and iso3 not in iso3_include)
        or (iso3_exclude and iso3 in iso3_exclude)
    )


def to_parquet(output_path: Path) -> None:
    """Convert to GeoParquet."""
    run(
        [
            *["gdal", "vector", "select"],
            *[output_path, output_path.with_suffix(".parquet")],
            *["--exclude", "fid"],
            "--overwrite",
            "--lco=COMPRESSION=ZSTD",
        ],
        check=False,
    )
    output_path.unlink()
