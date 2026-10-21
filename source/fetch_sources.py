"""Download raw open data for the Métropole de Lyon and store it as CSV under source/raw/.

Usage (from the repository root, root .venv):
    .venv/bin/python source/fetch_sources.py              # every source
    .venv/bin/python source/fetch_sources.py gbfs lyon    # only some sources

"Raw" means: values exactly as published, only filtered to the Lyon perimeter and converted
to CSV. Original files are kept in source/_archives/ (not versioned). Each written CSV is
listed in source/manifest.csv with its URL, licence, retrieval time, size and SHA-256.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import sys
import time
import traceback
import zipfile

import pandas as pd
import requests
from shapely import wkt
from shapely.geometry import Point
from shapely.ops import transform
from shapely.prepared import prep

SOURCE_DIR = Path(__file__).resolve().parent
ARCHIVES = SOURCE_DIR / "_archives"
MANIFEST = SOURCE_DIR / "manifest.csv"
USER_AGENT = "Mozilla/5.0 (Hackathon-Epitech-Citiz; open data collection)"
LYON_EPCI = "200046977"
GEOPF_WFS = "https://data.geopf.fr/wfs/ows"
GRANDLYON_WFS = "https://data.grandlyon.com/geoserver/metropole-de-lyon/ows"

LICENCES = {
    "lov2": "Licence Ouverte v2.0 (Etalab)",
    "odbl": "ODbL 1.0",
    "insee": "Licence Ouverte v2.0 (conditions de réutilisation INSEE)",
    "ign": "Licence Ouverte v2.0 (IGN)",
    "grandlyon": "Licence Ouverte v2.0 (data.grandlyon.com, à confirmer couche par couche)",
    "gbfs": "Licence du flux, voir system_information / transport.data.gouv.fr",
}

_manifest_rows = []


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------

def now_utc():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def http_get(url, params=None, stream=False, timeout=600, attempts=3):
    """GET with a browser-like user agent and simple retries."""
    for attempt in range(attempts):
        try:
            response = requests.get(url, params=params, headers={"User-Agent": USER_AGENT},
                                    timeout=timeout, stream=stream)
            response.raise_for_status()
            return response
        except requests.RequestException:
            if attempt == attempts - 1:
                raise
            time.sleep(10 * (attempt + 1))


def archive(url, name, params=None, refresh=False):
    """Download a file once into _archives/ and return its path."""
    path = ARCHIVES / name
    if path.exists() and not refresh:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    with http_get(url, params=params, stream=True) as response:
        tmp = path.with_suffix(path.suffix + ".part")
        with open(tmp, "wb") as handle:
            for chunk in response.iter_content(1 << 20):
                handle.write(chunk)
        tmp.rename(path)
    return path


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(frame, relative_path, *, source, url, licence, note=""):
    """Write a CSV (UTF-8, comma) under raw/ and record it in the manifest."""
    relative_path = f"raw/{relative_path}"
    path = SOURCE_DIR / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    _manifest_rows.append({
        "file": relative_path, "source": source, "url": url, "licence": LICENCES.get(licence, licence),
        "retrieved_at_utc": now_utc(), "rows": len(frame), "columns": frame.shape[1],
        "size_bytes": path.stat().st_size, "sha256": sha256(path), "note": note,
    })
    print(f"  wrote {relative_path}: {len(frame)} rows x {frame.shape[1]} cols")
    return path


def save_manifest():
    """Merge this run's rows into manifest.csv (one row per file, latest wins)."""
    old = pd.read_csv(MANIFEST, dtype=str) if MANIFEST.exists() else pd.DataFrame()
    new = pd.DataFrame(_manifest_rows, dtype=str)
    merged = pd.concat([old, new], ignore_index=True).drop_duplicates("file", keep="last")
    merged.sort_values("file").to_csv(MANIFEST, index=False)


def json_cells(frame):
    """Serialise nested lists/dicts so they survive a CSV round trip."""
    for column in frame.columns:
        if frame[column].map(lambda v: isinstance(v, (list, dict))).any():
            frame[column] = frame[column].map(
                lambda v: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v)
    return frame


# ---------------------------------------------------------------------------
# Perimeter: Métropole de Lyon
# ---------------------------------------------------------------------------

def swap_lat_lon(geometry):
    """Géoplateforme CSV gives EPSG:4326 coordinates as (lat, lon); shapely wants (lon, lat)."""
    return transform(lambda x, y, z=None: (y, x), geometry)


def ign_wfs_csv(layer, cql_filter, archive_name):
    params = {"SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature", "TYPENAMES": layer,
              "OUTPUTFORMAT": "csv", "CQL_FILTER": cql_filter}
    path = archive(GEOPF_WFS, archive_name, params=params)
    return pd.read_csv(path, dtype=str)


_perimeter = {}


def perimeter():
    """Return Lyon commune codes (incl. arrondissements), polygon and bbox (lon/lat)."""
    if _perimeter:
        return _perimeter
    epci = ign_wfs_csv("ADMINEXPRESS-COG.LATEST:epci", f"code_siren='{LYON_EPCI}'", "ign_epci_lyon.csv")
    polygon = swap_lat_lon(wkt.loads(epci.loc[0, "geometrie"]))
    communes = epci.loc[0, "codes_insee_des_communes_membres"].split("/")
    arrondissements = [f"6938{i}" for i in range(1, 10)]
    _perimeter.update(
        epci=epci, polygon=polygon, prepared=prep(polygon), bbox=polygon.bounds,
        communes=communes, codes=set(communes) | set(arrondissements), arrondissements=arrondissements,
    )
    return _perimeter


def in_lyon(lon, lat):
    p = perimeter()
    minx, miny, maxx, maxy = p["bbox"]
    if not (minx <= lon <= maxx and miny <= lat <= maxy):
        return False
    return p["prepared"].contains(Point(lon, lat))


def points_in_lyon(frame, lon="lon", lat="lat"):
    lons = pd.to_numeric(frame[lon], errors="coerce")
    lats = pd.to_numeric(frame[lat], errors="coerce")
    mask = [False if pd.isna(x) or pd.isna(y) else in_lyon(x, y) for x, y in zip(lons, lats)]
    return frame.loc[mask]


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

GEOGRAPHY_DIR = "geography(lyon metropole)"


def fetch_geography():
    """IGN ADMIN EXPRESS (EPCI, communes, arrondissements) and IRIS contours."""
    p = perimeter()
    url = "https://geoservices.ign.fr/adminexpress"
    note = "geometrie en WKT, EPSG:4326, ordre des axes (latitude longitude)"
    write_csv(p["epci"], f"{GEOGRAPHY_DIR}/ign_adminexpress_epci_lyon.csv",
              source="IGN ADMIN EXPRESS COG (WFS Géoplateforme)", url=url, licence="ign", note=note)
    codes = ",".join(f"'{c}'" for c in sorted(p["communes"]))
    communes = ign_wfs_csv("ADMINEXPRESS-COG.LATEST:commune", f"code_insee IN ({codes})", "ign_communes_lyon.csv")
    write_csv(communes, f"{GEOGRAPHY_DIR}/ign_adminexpress_communes_lyon.csv", source="IGN ADMIN EXPRESS COG",
              url=url, licence="ign", note=note)
    arr = ",".join(f"'{c}'" for c in p["arrondissements"])
    arrondissements = ign_wfs_csv("ADMINEXPRESS-COG.LATEST:arrondissement_municipal", f"code_insee IN ({arr})",
                                  "ign_arrondissements_lyon.csv")
    write_csv(arrondissements, f"{GEOGRAPHY_DIR}/ign_adminexpress_arrondissements_lyon.csv",
              source="IGN ADMIN EXPRESS COG", url=url, licence="ign", note=note)
    all_codes = ",".join(f"'{c}'" for c in sorted(p["codes"]))
    iris = ign_wfs_csv("STATISTICALUNITS.IRIS:contours_iris", f"code_insee IN ({all_codes})", "ign_iris_lyon.csv")
    write_csv(iris, f"{GEOGRAPHY_DIR}/ign_contours_iris_lyon.csv", source="IGN Contours IRIS (WFS Géoplateforme)",
              url="https://geoservices.ign.fr/contoursiris", licence="ign", note=note)


# system -> (gbfs.json index, output folder under raw/, feeds kept)
GBFS_SYSTEMS = {
    "citiz_metropole_lyon": ("https://backend.citiz.fr/public/provider/3/gbfs/3.0/gbfs.json", "citiz",
                             ["station_information", "vehicle_status", "vehicle_types", "system_pricing_plans"]),
    "leoandgo": ("https://download.data.grandlyon.com/files/rdata/lag_leoandgo.disponibilite/gbfs.json",
                 "concurence/leodango", ["free_bike_status", "geofencing_zones"]),
    "getaround_lyon": ("https://getaround.com/gbfs/v3/lyon/gbfs", "concurence/getaround_lyon", ["vehicle_status"]),
}
# GBFS list payloads, in the order they are looked for inside "data".
GBFS_LIST_KEYS = ["stations", "vehicles", "bikes", "vehicle_types", "plans", "regions", "alerts", "versions",
                  "rental_hours", "calendars"]


def gbfs_feed_urls(index):
    data = index.get("data", {})
    if "feeds" in data:                                   # GBFS 3.0
        return {f["name"]: f["url"] for f in data["feeds"]}
    language = "fr" if "fr" in data else next(iter(data))  # GBFS 2.x: one block per language
    return {f["name"]: f["url"] for f in data[language]["feeds"]}


def gbfs_to_frame(payload):
    data = payload.get("data", {})
    if "geofencing_zones" in data:
        features = data["geofencing_zones"].get("features", [])
        frame = pd.json_normalize(features, max_level=1)
    else:
        key = next((k for k in GBFS_LIST_KEYS if isinstance(data.get(k), list)), None)
        frame = pd.json_normalize(data[key], max_level=1) if key else pd.json_normalize(data, max_level=0)
    frame = json_cells(frame)
    frame["gbfs_last_updated"] = payload.get("last_updated")
    frame["gbfs_version"] = payload.get("version")
    return frame


def fetch_gbfs():
    """Selected feeds of Citiz and its car-sharing competitors (Leo&Go, Getaround), one CSV per feed."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for system, (index_url, folder, kept) in GBFS_SYSTEMS.items():
        print(f" GBFS {system}")
        try:
            index_path = archive(index_url, f"gbfs/{system}/{stamp}/gbfs.json", refresh=True)
            feeds = gbfs_feed_urls(json.loads(index_path.read_text()))
        except Exception as error:  # a failing operator must not stop the others
            print(f"  ! {system}: {error}")
            continue
        for name in kept:
            if name not in feeds:
                print(f"  ! {system}/{name}: feed not published")
                continue
            try:
                path = archive(feeds[name], f"gbfs/{system}/{stamp}/{name}.json", refresh=True)
                frame = gbfs_to_frame(json.loads(path.read_text()))
                frame.insert(0, "system", system)
                write_csv(frame, f"{folder}/{name}.csv", source=f"GBFS {system}", url=feeds[name],
                          licence="gbfs", note=f"instantané {stamp}")
            except Exception as error:
                print(f"  ! {system}/{name}: {error}")


def fetch_public_transit():
    """SNCF GTFS stops in Lyon, SNCF passenger stations and their yearly ridership."""
    p = perimeter()
    # SNCF national GTFS (TGV, Intercités, TER): Lyon stops and their parent stations.
    url = "https://eu.ftp.opendatasoft.com/sncf/plandata/Export_OpenData_SNCF_GTFS_NewTripId.zip"
    with zipfile.ZipFile(archive(url, "sncf_gtfs.zip")) as gtfs:
        stops = pd.read_csv(gtfs.open("stops.txt"), dtype=str)
    lyon_stops = points_in_lyon(stops, "stop_lon", "stop_lat")
    stop_ids = set(lyon_stops["stop_id"]) | set(lyon_stops["parent_station"].dropna())
    write_csv(stops.loc[stops["stop_id"].isin(stop_ids)], "public_transit/stops.csv",
              source="SNCF GTFS TGV/Intercités/TER", url=url, licence="odbl",
              note="arrêts situés dans la Métropole et leurs gares parentes")

    export = "https://ressources.data.sncf.com/api/explore/v2.1/catalog/datasets/{}/exports/csv"
    stations = pd.read_csv(archive(export.format("gares-de-voyageurs"), "sncf_gares_de_voyageurs.csv",
                                   params={"delimiter": ";"}), sep=";", dtype=str)
    stations = stations.loc[stations["codeinsee"].isin(p["codes"])]
    write_csv(stations, "public_transit/sncf_gares_de_voyageurs_lyon.csv", source="SNCF gares-de-voyageurs",
              url=export.format("gares-de-voyageurs"), licence="odbl")
    ridership = pd.read_csv(archive(export.format("frequentation-gares"), "sncf_frequentation_gares.csv",
                                    params={"delimiter": ";"}), sep=";", dtype=str)
    uic = set(stations["codes_uic"].str.split(";").explode())
    write_csv(ridership.loc[ridership["code_uic_complet"].isin(uic)], "public_transit/sncf_frequentation_gares_lyon.csv",
              source="SNCF frequentation-gares", url=export.format("frequentation-gares"), licence="odbl")


def fetch_population():
    """INSEE Filosofi 2021 200 m grid, restricted to the Métropole."""
    p = perimeter()
    url = "https://www.insee.fr/fr/statistiques/fichier/8735162/Filosofi2021_carreaux_200m_csv.zip"
    with zipfile.ZipFile(archive(url, "Filosofi2021_carreaux_200m_csv.zip")) as z:
        name = next(n for n in z.namelist() if n.endswith(".csv") and "met" in n.lower())
        keep = []
        for chunk in pd.read_csv(z.open(name), dtype=str, chunksize=500_000):
            codes = chunk["lcog_geo"].fillna("")
            mask = codes.map(lambda value: any(code.strip() in p["codes"] for code in value.split(",")))
            keep.append(chunk.loc[mask])
    write_csv(pd.concat(keep, ignore_index=True), "population/insee_filosofi2021_carreaux_200m_lyon.csv",
              source="INSEE Filosofi 2021 carreaux 200 m", url="https://www.insee.fr/fr/statistiques/8735162",
              licence="insee", note=f"fichier {name} ; carreaux dont lcog_geo contient une commune de la Métropole")


GRANDLYON_LAYERS = {
    "parkings": "pvo_patrimoine_voirie.pvoparking",
    "zfe_perimetre": "eco_ecologie.zfe",
    "bornes_irve": "nrj_energie.irve",
    "quartiers_prioritaires_2024_2030": "ter_territoire.quartier_prioritaire_2024_2030",
}


def fetch_lyon():
    """Open layers of the Métropole de Lyon WFS, exported as CSV (geometry in WKT)."""
    for name, layer in GRANDLYON_LAYERS.items():
        params = {"SERVICE": "WFS", "VERSION": "2.0.0", "REQUEST": "GetFeature",
                  "TYPENAME": f"metropole-de-lyon:{layer}", "OUTPUTFORMAT": "CSV", "SRSNAME": "EPSG:4326"}
        try:
            path = archive(GRANDLYON_WFS, f"grandlyon/{name}.csv", params=params)
            if path.read_bytes()[:5] == b"<?xml":
                path.unlink()
                raise RuntimeError("WFS exception (layer protected or unknown)")
            frame = pd.read_csv(path, dtype=str, low_memory=False)
        except Exception as error:
            print(f"  ! grandlyon {name}: {error}")
            continue
        write_csv(frame, f"lyon/{name}.csv", source=f"data.grandlyon.com WFS {layer}",
                  url=f"https://data.grandlyon.com (couche metropole-de-lyon:{layer})", licence="grandlyon",
                  note="géométrie en WKT, EPSG:4326 (lon lat)")


SOURCES = {
    "geography": fetch_geography, "gbfs": fetch_gbfs, "public_transit": fetch_public_transit,
    "population": fetch_population, "lyon": fetch_lyon,
}


def main(selected):
    ARCHIVES.mkdir(parents=True, exist_ok=True)
    failures = {}
    for name in selected or SOURCES:
        print(f"== {name}", flush=True)
        try:
            SOURCES[name]()
        except Exception:
            failures[name] = traceback.format_exc()
            print(failures[name])
        finally:
            save_manifest()
            _manifest_rows.clear()
    for name, error in failures.items():
        print(f"FAILED {name}: {error.strip().splitlines()[-1]}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
