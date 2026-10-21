"""Shared helpers for the siting-data notebooks: paths, region, cached downloads."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import time

import geopandas as gpd
import pandas as pd
import requests

AURA_DEPARTMENTS = ["01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"]
USER_AGENT = "Hackathon-Epitech-Citiz/1.0 (student project, open data)"
OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
DEPARTMENTS_URL = (
    "https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/"
    "departements-version-simplifiee.geojson"
)


def project_root():
    """Return the repository root, wherever the notebook is started from."""
    here = Path.cwd().resolve()
    return next(d for d in [here, *here.parents] if (d / "siting-data" / "siting_sources.py").is_file())


def module_paths():
    """Return the raw and clean data folders of the module, created if needed."""
    root = project_root()
    raw = root / "siting-data/data/raw"
    clean = root / "siting-data/data/clean"
    raw.mkdir(parents=True, exist_ok=True)
    clean.mkdir(parents=True, exist_ok=True)
    return root, raw, clean


def load_region():
    """Return the IGN Auvergne-Rhône-Alpes outline versioned by regional-data (EPSG:4326)."""
    path = project_root() / "regional-data/data/processed/aura_region.geojson"
    return gpd.read_file(path).to_crs(4326).geometry.iloc[0]


def load_departments():
    """Return the 12 AURA departments (code, name, geometry) from the simplified IGN contours."""
    _, raw, _ = module_paths()
    path = download(DEPARTMENTS_URL, raw / "departements.geojson")
    departments = gpd.read_file(path).to_crs(4326)
    departments = departments.rename(columns={"code": "department_code", "nom": "department_name"})
    return departments.loc[departments["department_code"].isin(AURA_DEPARTMENTS),
                           ["department_code", "department_name", "geometry"]].reset_index(drop=True)


def assign_department(points, departments, max_distance_m=2000):
    """Add the department of each point; points just outside the simplified contours get the nearest one."""
    joined = gpd.sjoin(points, departments, how="left", predicate="within").drop(columns="index_right")
    joined = joined.loc[~joined.index.duplicated()]
    missing = joined["department_code"].isna()
    joined["department_method"] = missing.map({False: "within", True: pd.NA})
    if missing.any():
        nearest = gpd.sjoin_nearest(points.loc[missing, ["geometry"]].to_crs(2154), departments.to_crs(2154),
                                    how="left", max_distance=max_distance_m)
        nearest = nearest.loc[~nearest.index.duplicated()]
        joined.loc[nearest.index, ["department_code", "department_name"]] = nearest[["department_code", "department_name"]]
        joined.loc[nearest.index[nearest["department_code"].notna()], "department_method"] = "nearest"
    return joined


def _record_download(path, url, description):
    """Append the file's origin, date and SHA-256 to data/raw/download_manifest.json."""
    manifest_path = path.parent / "download_manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    manifest[path.name] = {
        "url": url,
        "description": description,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "size_bytes": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


def download(url, path, params=None, description="", refresh=False):
    """Download a file once; later runs reuse the local copy unless refresh=True."""
    path = Path(path)
    if path.exists() and not refresh:
        return path
    response = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=600)
    response.raise_for_status()
    path.write_bytes(response.content)
    _record_download(path, response.url, description)
    return path


def fetch_overpass(query, path, description="", refresh=False, attempts=3):
    """Run an Overpass query once and keep the JSON answer, trying a mirror if needed."""
    path = Path(path)
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    last_error = None
    for attempt in range(attempts):
        url = OVERPASS_URLS[attempt % len(OVERPASS_URLS)]
        try:
            response = requests.post(url, data={"data": query}, headers={"User-Agent": USER_AGENT}, timeout=1000)
            response.raise_for_status()
            payload = response.json()
            if "remark" in payload and "error" in payload["remark"].lower():
                raise RuntimeError(payload["remark"])
            path.write_text(json.dumps(payload))
            _record_download(path, url, description + " | query: " + " ".join(query.split()))
            return payload
        except (requests.RequestException, RuntimeError, ValueError) as error:
            last_error = error
            print(f"Overpass attempt {attempt + 1} failed on {url}: {error}")
            time.sleep(30)
    raise RuntimeError(f"Overpass query failed after {attempts} attempts") from last_error
