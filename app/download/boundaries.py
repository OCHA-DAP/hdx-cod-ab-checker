from pathlib import Path
from re import search

from tenacity import retry, stop_after_attempt, wait_fixed
from tqdm import tqdm

from ..config import ARCGIS_SERVICE_REGEX, ARCGIS_SERVICE_URL, ATTEMPT, WAIT, data_dir
from ..utils import client_get, is_iso3_allowed
from .utils import download_feature


@retry(stop=stop_after_attempt(ATTEMPT), wait=wait_fixed(WAIT))
def download_layers(output_dir: Path, url: str, params: dict, layers: dict) -> None:
    """Download all ESRIJSON from a Feature Service."""
    for layer in layers:
        if layer["type"] == "Feature Layer":
            feature_url = f"{url}/{layer['id']}"
            response = client_get(feature_url, params).json()
            download_feature(output_dir, feature_url, params, response)


@retry(stop=stop_after_attempt(ATTEMPT), wait=wait_fixed(WAIT))
def main(token: str) -> None:
    """Download all ESRIJSON from Feature Services."""
    params = {"f": "json", "token": token}
    response = client_get(ARCGIS_SERVICE_URL, params).json()
    services = [
        x
        for x in response["services"]
        if x["type"] == "FeatureServer" and search(ARCGIS_SERVICE_REGEX, x["name"])
    ]
    pbar = tqdm(services)
    for service in pbar:
        pbar.set_postfix_str(service["name"].split("/")[-1])
        service_name = service["name"].split("/")[-1]
        iso3 = service_name[7:10].upper()
        if not is_iso3_allowed(iso3):
            continue
        output_dir = data_dir / "boundaries" / service_name
        service_url = f"{ARCGIS_SERVICE_URL}/{service_name}/FeatureServer"
        layers = client_get(service_url, params).json()["layers"]
        download_layers(output_dir, service_url, params, layers)
