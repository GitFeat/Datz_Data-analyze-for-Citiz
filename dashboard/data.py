"""Tables locales et jointure contrôlée, sans modifier les sources."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLES = {
    "Stations et équipements croisés (AURA)": "regional-data/data/processed/station_features.csv",
    "Stations Citiz (France)": "output/citiz_stations_geo.csv",
    "Disponibilité Citiz (instantané)": "output/citiz_station_status.csv",
    "Catalogue des lieux OSM (AURA)": "regional-data/data/processed/osm_aura_table.csv",
}


def load_table(label):
    frame = pd.read_csv(ROOT / TABLES[label], low_memory=False)
    if label == "Stations et équipements croisés (AURA)":
        stations = pd.read_csv(ROOT / TABLES["Stations Citiz (France)"], low_memory=False)
        columns = ["station_uid", "city", "departement", "region", "reseau", "capacity",
                   "num_vehicles_available", "is_renting", "extracted_at"]
        stations = stations[[c for c in columns if c in stations.columns]]
        if frame.station_uid.isna().any() or stations.station_uid.isna().any():
            raise ValueError("Une station sans identifiant empêche une jointure fiable.")
        frame = frame.merge(stations, on="station_uid", how="left", validate="one_to_one",
                            indicator="station_reference_match")
        frame["station_reference_match"] = frame.station_reference_match.astype(str)
    return frame
