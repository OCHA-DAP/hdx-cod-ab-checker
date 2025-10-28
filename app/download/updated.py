from datetime import datetime
from re import search

from defusedxml.ElementTree import fromstring
from pandas import DataFrame
from tqdm import tqdm

from ..config import ARCGIS_SERVICE_REGEX, ARCGIS_SERVICE_URL, data_dir
from ..utils import client_get


def main(token: str) -> None:
    """Download all ESRIJSON from Feature Services."""
    params = {"f": "json", "token": token}
    response = client_get(ARCGIS_SERVICE_URL, params).json()
    services = [
        x
        for x in response["services"]
        if x["type"] == "FeatureServer" and search(ARCGIS_SERVICE_REGEX, x["name"])
    ]
    metadata_summary = []
    pbar = tqdm(services)
    for service in pbar:
        pbar.set_postfix_str(service["name"][14:17].upper())
        service_name = service["name"].split("/")[-1]
        metadata_url = (
            f"{ARCGIS_SERVICE_URL}/{service_name}/FeatureServer/info/metadata"
        )
        metadata = client_get(metadata_url, params)
        element = fromstring(metadata.text)
        creadate = element.find("Esri/CreaDate")
        creatime = element.find("Esri/CreaTime")
        date_obj = None
        if creadate is not None and creatime is not None:
            date_str = f"{creadate.text}{creatime.text}0000"
            date_obj = datetime.strptime(date_str, "%Y%m%d%H%M%S%f")  # noqa: DTZ007
        metadata_summary.append({"service": service_name, "updated": date_obj})
    df = DataFrame(metadata_summary)
    df = df.sort_values("updated", ascending=False)
    df = df.reset_index(drop=True)
    df.to_parquet(data_dir / "updated.parquet", compression="zstd")
    df.to_csv(data_dir / "updated.csv", index=False, encoding="utf-8-sig")
