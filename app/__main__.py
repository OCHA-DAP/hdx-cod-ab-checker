import logging
from pathlib import Path

from . import attributes, images
from .checks import __main__ as checks
from .config import (
    ARCGIS_CHECK,
    ARCGIS_DOWNLOAD,
    RUN_CHECKS,
    RUN_IMAGES,
    RUN_SCORES,
    data_dir,
)
from .download.boundaries import main as download_boundaries
from .download.meta import main as download_meta
from .download.updated import main as download_updated
from .scores import __main__ as scores
from .style import __main__ as style
from .utils import generate_token

logger = logging.getLogger(__name__)
cwd = Path(__file__).parent


def main() -> None:
    """Generate datasets and create them in HDX."""
    data_dir.mkdir(parents=True, exist_ok=True)
    token = generate_token()
    if ARCGIS_CHECK:
        download_meta(token)
        download_updated(token)
    if ARCGIS_DOWNLOAD:
        download_boundaries(token)
    if RUN_CHECKS:
        checks.main()
    if RUN_SCORES:
        scores.main()
        style.main()
    if RUN_IMAGES:
        attributes.main()
        images.main()


if __name__ == "__main__":
    main()
