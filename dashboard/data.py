"""Tables locales, lues sans modification des sources."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = {
    "Stations et équipements croisés (AURA)": "regional-data/data/release/citiz_aura_final.csv",
    "Stations Citiz (France)": "output/citiz_stations_geo.csv",
    "Disponibilité Citiz (instantané)": "output/citiz_station_status.csv",
    "Catalogue des lieux OSM (AURA)": "regional-data/data/processed/osm_aura_table.csv",
}


def load_table(label):
    """The AURA table is the release built by regional-data/notebooks/07: the join is already done and checked there."""
    encoding = "utf-8-sig" if label == "Stations et équipements croisés (AURA)" else "utf-8"
    return pd.read_csv(ROOT / TABLES[label], low_memory=False, encoding=encoding)
