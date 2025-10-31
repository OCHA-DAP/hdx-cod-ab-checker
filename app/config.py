import logging
from os import environ, getenv
from pathlib import Path

from dotenv import load_dotenv
from pandas import read_csv

load_dotenv(override=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("httpx").setLevel(logging.WARNING)

environ["OGR_GEOJSON_MAX_OBJ_SIZE"] = "0"
environ["OGR_ORGANIZE_POLYGONS"] = "ONLY_CCW"
environ["PYOGRIO_USE_ARROW"] = "1"


def is_bool(value: str) -> bool:
    """Convert string option on env variable to boolean."""
    return value.lower() in ("yes", "on", "true", "1")


OBJECTID = "esriFieldTypeOID"

ARCGIS_SERVER = getenv("ARCGIS_SERVER", "https://gis.unocha.org")
ARCGIS_USERNAME = getenv("ARCGIS_USERNAME", "")
ARCGIS_PASSWORD = getenv("ARCGIS_PASSWORD", "")
ARCGIS_FOLDER = getenv("ARCGIS_FOLDER", "Hosted")
ARCGIS_SERVICE_URL = f"{ARCGIS_SERVER}/server/rest/services/{ARCGIS_FOLDER}"
ARCGIS_SERVICE_REGEX = getenv("ARCGIS_SERVICE_REGEX", r"cod_ab_[a-z]{3}")
ARCGIS_SERVICE_LATEST_REGEX = getenv("ARCGIS_SERVICE_REGEX", r"cod_ab_[a-z]{3}$")

ARCGIS_LAYER_REGEX = getenv("ARCGIS_LAYER_REGEX", r"^[a-z]{3}_admin\d$")
ARCGIS_METADATA = getenv("ARCGIS_METADATA", "COD_Global_Metadata")
ARCGIS_METADATA_URL = f"{ARCGIS_SERVICE_URL}/{ARCGIS_METADATA}/FeatureServer/0"

ARCGIS_CHECK = is_bool(getenv("ARCGIS_CHECK", "NO"))
ARCGIS_DOWNLOAD = is_bool(getenv("ARCGIS_DOWNLOAD", "NO"))
RUN_CHECKS = is_bool(getenv("RUN_CHECKS", "NO"))
RUN_SCORES = is_bool(getenv("RUN_SCORES", "NO"))
RUN_IMAGES = is_bool(getenv("RUN_IMAGES", "NO"))

ATTEMPT = int(getenv("ATTEMPT", "5"))
WAIT = int(getenv("WAIT", "10"))
TIMEOUT = int(getenv("TIMEOUT", "60"))
TIMEOUT_DOWNLOAD = int(getenv("TIMEOUT_DOWNLOAD", "600"))
EXPIRATION = int(getenv("EXPIRATION", "1440"))  # minutes (1 day)

ADMIN_LEVEL_MAX = 5

EPSG_EQUAL_AREA = 6933
EPSG_WGS84 = 4326
GEOJSON_PRECISION = 6
METERS_PER_KM = 1_000_000
POLYGON = "Polygon"
SLIVER_GAP_AREA_KM = 0.000_1
SLIVER_GAP_THINNESS = 0.001
VALID_GEOMETRY = "Valid Geometry"

ISO3_INCLUDE = getenv("ISO3_INCLUDE", "").upper()
ISO3_EXCLUDE = getenv("ISO3_EXCLUDE", "").upper()

cwd = Path(__file__).parent
m49_df = read_csv(cwd / "m49.csv")
m49 = {x["iso3"]: x for x in m49_df.to_dict("records")}

official_languages = ["ar", "en", "es", "fr", "ru", "zh"]
romanized_languages = ["en", "es", "fr", "hu", "id", "nl", "pl", "pt", "ro", "sk"]

data_dir = cwd / "../data"
data_dir.mkdir(parents=True, exist_ok=True)
