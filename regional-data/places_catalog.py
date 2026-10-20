"""Build a regional catalog of useful mapped OSM objects."""
from pathlib import Path
import hashlib
import json

import geopandas as gpd
import osmium
import pandas as pd
from shapely import wkb

# The first matching tag defines the primary category. Other matches are preserved.
CATEGORY_LABELS = {
    "food_and_drink": "Restauration et boissons",
    "education": "Éducation",
    "health": "Santé",
    "mobility": "Mobilité et stationnement",
    "public_services": "Services publics et collectifs",
    "finance": "Banques et services financiers",
    "culture_and_community": "Culture et vie collective",
    "retail": "Commerces",
    "professional_services": "Bureaux et services professionnels",
    "craft": "Artisanat",
    "tourism": "Tourisme et hébergement",
    "sports_and_leisure": "Sport et loisirs",
    "heritage": "Patrimoine",
    "nature": "Nature et paysage",
    "water": "Eau et hydrographie",
    "emergency": "Secours et sécurité",
    "infrastructure": "Infrastructures et repères",
    "settlement": "Villes, villages et lieux-dits",
    "other_amenities": "Autres équipements et services",
}
AMENITY_GROUPS = {
    "food_and_drink": "restaurant cafe bar pub fast_food food_court ice_cream biergarten",
    "education": "school kindergarten college university language_school music_school driving_school research_institute training",
    "health": "hospital clinic doctors dentist pharmacy nursing_home social_facility baby_hatch",
    "mobility": "parking parking_entrance parking_space bicycle_parking bicycle_rental bicycle_repair_station charging_station fuel bus_station car_sharing car_rental taxi motorcycle_parking ferry_terminal vehicle_inspection",
    "public_services": "townhall courthouse prison post_office post_box recycling waste_disposal waste_transfer_station toilets drinking_water water_point shelter public_bath shower childcare animal_shelter",
    "finance": "bank atm bureau_de_change payment_terminal",
    "culture_and_community": "library cinema theatre arts_centre community_centre conference_centre events_venue place_of_worship public_bookcase studio",
    "emergency": "police fire_station rescue_station ranger_station",
}
AMENITY_LOOKUP = {value: category for category, values in AMENITY_GROUPS.items() for value in values.split()}
SELECTED_VALUES = {
    "railway": set("station halt tram_stop subway_entrance funicular".split()),
    "highway": set("bus_stop services rest_area elevator trailhead".split()),
    "natural": set("peak saddle volcano cave_entrance spring hot_spring waterfall beach bay cape peninsula island islet glacier lake cliff rock stone arch".split()),
    "waterway": set("river stream canal waterfall dam weir dock lock_gate".split()),
    "water": set("lake reservoir pond basin lagoon river canal stream_pool oxbow".split()),
    "man_made": set("tower lighthouse water_tower watermill windmill observatory works wastewater_plant water_works pumping_station dam pier bridge communications_tower".split()),
    "place": set("city town village hamlet suburb quarter neighbourhood isolated_dwelling locality island islet".split()),
    "aeroway": set("aerodrome terminal helipad gate".split()),
    "aerialway": {"station"},
}
TAG_ORDER = ["amenity", "healthcare", "shop", "office", "craft", "tourism", "leisure", "sport", "historic", "public_transport", "railway", "highway", "aeroway", "aerialway", "emergency", "natural", "waterway", "water", "man_made", "place", "mountain_pass"]
BROAD_TAG_GROUPS = {
    "healthcare": "health", "shop": "retail", "office": "professional_services",
    "craft": "craft", "tourism": "tourism", "leisure": "sports_and_leisure",
    "sport": "sports_and_leisure", "historic": "heritage", "public_transport": "mobility",
    "railway": "mobility", "highway": "mobility", "aeroway": "mobility",
    "aerialway": "mobility", "emergency": "emergency", "natural": "nature",
    "waterway": "water", "water": "water", "man_made": "infrastructure",
    "place": "settlement", "mountain_pass": "nature",
}
EXCLUDED_VALUES = {"no", "disused", "abandoned", "razed", "demolished", "construction", "proposed"}


def classify_tags(tags):
    """Return every matching category in a deterministic priority order."""
    matches = []
    for key in TAG_ORDER:
        value = tags.get(key)
        if not value or value in EXCLUDED_VALUES:
            continue
        if key in SELECTED_VALUES and value not in SELECTED_VALUES[key]:
            continue
        if key == "mountain_pass" and value != "yes":
            continue
        category = AMENITY_LOOKUP.get(value, "other_amenities") if key == "amenity" else BROAD_TAG_GROUPS[key]
        matches.append({"broad_category": category, "point_category": f"{key}={value}", "tag_key": key, "tag_value": value})
    return matches


def read_source(path, counting_area, region):
    """Read nodes, ways and assembled areas without converting lines into polygons."""
    factory = osmium.geom.WKBFactory()
    records, errors, expected_relations, found_relations = {}, [], set(), set()
    processor = osmium.FileProcessor(str(path)).with_locations().with_areas()
    processor = processor.with_filter(osmium.filter.KeyFilter(*TAG_ORDER))
    for item in processor:
        tags = dict(item.tags)
        matches = classify_tags(tags)
        if not matches:
            continue
        if item.is_relation():
            if tags.get("type") in {"multipolygon", "boundary"}:
                expected_relations.add(f"relation/{item.id}")
            else:
                errors.append({"source_file": path.name, "osm_uid": f"relation/{item.id}", "reason": "Non-area relation: geometry not reconstructed"})
            continue
        if item.is_area():
            object_type = "way" if item.from_way() else "relation"
            object_id = item.orig_id()
            if object_type == "relation":
                found_relations.add(f"relation/{object_id}")
        elif item.is_node():
            object_type, object_id = "node", item.id
        elif item.is_way():
            object_type, object_id = "way", item.id
        else:
            continue
        uid = f"{object_type}/{object_id}"
        try:
            if item.is_node():
                geometry = wkb.loads(factory.create_point(item.location), hex=True)
            elif item.is_area():
                geometry = wkb.loads(factory.create_multipolygon(item), hex=True)
            else:
                geometry = wkb.loads(factory.create_linestring(item), hex=True)
            if geometry.is_empty or not geometry.is_valid:
                raise ValueError("Empty or invalid geometry")
        except (RuntimeError, ValueError, osmium.InvalidLocationError) as error:
            errors.append({"source_file": path.name, "osm_uid": uid, "reason": str(error)})
            continue
        if not geometry.intersects(counting_area):
            continue
        primary = matches[0]
        records[uid] = {
            "osm_uid": uid, "osm_type": object_type, "osm_id": str(object_id),
            "osm_version": item.version, "name": tags.get("name", ""),
            "broad_category": primary["broad_category"],
            "point_category": primary["point_category"],
            "category_matches_json": json.dumps(matches, ensure_ascii=False),
            "tags_json": json.dumps(tags, ensure_ascii=False, sort_keys=True),
            "access": tags.get("access", ""), "operator": tags.get("operator", ""),
            "source_files": path.name, "inside_region": geometry.intersects(region),
            "geometry": geometry,
        }
    for uid in expected_relations - found_relations:
        errors.append({"source_file": path.name, "osm_uid": uid, "reason": "Tagged multipolygon relation not reconstructed"})
    return list(records.values()), errors


def build_catalog(project_directory):
    """Extract and export the catalog, reusing a cache only for identical inputs."""
    project_directory = Path(project_directory)
    output = project_directory / "regional-data/data/processed"
    paths = [project_directory / f"ign-osm/data/raw/osm/{name}-261016.osm.pbf" for name in ["auvergne", "rhone-alpes"]]
    area_path = output / "aura_counting_area.geojson"
    signature = {
        "module_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources": [{"name": p.name, "size_bytes": p.stat().st_size, "modified_ns": p.stat().st_mtime_ns} for p in paths],
        "area_sha256": hashlib.sha256(area_path.read_bytes()).hexdigest(),
    }
    manifest_path = output / "osm_places_catalog_manifest.json"
    catalog_path = output / "osm_places_catalog.gpkg"
    required = [catalog_path, output / "osm_places_catalog.csv", output / "osm_places_taxonomy.csv", output / "osm_places_catalog_errors.csv"]
    if manifest_path.exists() and all(p.exists() for p in required):
        manifest = json.loads(manifest_path.read_text())
        if manifest["inputs"] == signature:
            print("Reusing the verified catalog exports.")
            return gpd.read_file(catalog_path), manifest
    region = gpd.read_file(output / "aura_region.geojson").to_crs(4326).geometry.iloc[0]
    counting_area = gpd.read_file(area_path).to_crs(4326).geometry.iloc[0]
    all_records, all_errors = [], []
    for path in paths:
        print(f"Reading {path.name}...", flush=True)
        records, errors = read_source(path, counting_area, region)
        all_records.extend(records)
        all_errors.extend(errors)
        print(f"Selected {len(records)} objects; logged {len(errors)} issues.", flush=True)
    objects = gpd.GeoDataFrame(all_records, geometry="geometry", crs=4326)
    source_files = objects.groupby("osm_uid")["source_files"].agg(lambda values: ",".join(sorted(set(values))))
    overlap_count = len(objects) - objects["osm_uid"].nunique()
    objects = objects.sort_values(["osm_uid", "osm_version"]).drop_duplicates("osm_uid", keep="last").reset_index(drop=True)
    objects["source_files"] = objects["osm_uid"].map(source_files)
    objects["geometry_type"] = objects.geometry.geom_type
    # Coordinates are display anchors, not building entrances or centroids.
    anchors = objects.to_crs(2154).geometry.representative_point().to_crs(4326)
    objects["longitude"] = anchors.x
    objects["latitude"] = anchors.y
    objects["countable"] = True
    objects["duplicate_of"] = ""
    metric = objects.to_crs(2154)
    areas = metric.loc[metric.geom_type.isin(["Polygon", "MultiPolygon"])]
    for index, point in metric.loc[metric.geom_type == "Point"].iterrows():
        if not point["name"].strip():
            continue
        for position in areas.sindex.query(point.geometry, predicate="intersects"):
            area = areas.iloc[position]
            if point["name"].strip().casefold() == area["name"].strip().casefold() and point["point_category"] == area["point_category"]:
                objects.loc[index, ["countable", "duplicate_of"]] = [False, area["osm_uid"]]
                break
    taxonomy_rows = {}
    for raw in objects["category_matches_json"]:
        for match in json.loads(raw):
            key = (match["broad_category"], match["point_category"])
            if key not in taxonomy_rows:
                taxonomy_rows[key] = {**match, "broad_category_label_fr": CATEGORY_LABELS[match["broad_category"]], "mapped_object_count": 0}
            taxonomy_rows[key]["mapped_object_count"] += 1
    taxonomy = pd.DataFrame(taxonomy_rows.values()).sort_values(["broad_category", "point_category"])
    errors = pd.DataFrame(all_errors, columns=["source_file", "osm_uid", "reason"])
    assert objects.osm_uid.is_unique and objects.geometry.is_valid.all()
    assert objects.geometry.intersects(counting_area).all()
    assert objects["broad_category"].isin(CATEGORY_LABELS).all()
    objects.to_file(catalog_path, layer="places", driver="GPKG")
    objects.drop(columns="geometry").to_csv(output / "osm_places_catalog.csv", index=False)
    taxonomy.to_csv(output / "osm_places_taxonomy.csv", index=False)
    errors.to_csv(output / "osm_places_catalog_errors.csv", index=False)
    manifest = {
        "inputs": signature, "object_count": len(objects), "overlap_rows_removed": overlap_count,
        "point_area_duplicates_flagged": int((~objects["countable"]).sum()),
        "issue_count": len(errors), "category_count": len(taxonomy),
        "broad_category_counts": objects.groupby("broad_category").size().to_dict(),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return objects, manifest


def verify_exports(project_directory, objects):
    """Check persisted IDs, geometry validity, coordinates and taxonomy coverage."""
    output = Path(project_directory) / "regional-data/data/processed"
    saved = gpd.read_file(output / "osm_places_catalog.gpkg")
    table = pd.read_csv(output / "osm_places_catalog.csv", keep_default_na=False)
    taxonomy = pd.read_csv(output / "osm_places_taxonomy.csv")
    assert set(saved.osm_uid) == set(objects.osm_uid) == set(table.osm_uid)
    assert saved.osm_uid.is_unique and saved.geometry.is_valid.all()
    assert saved.longitude.between(-180, 180).all() and saved.latitude.between(-90, 90).all()
    assert set(saved.point_category).issubset(set(taxonomy.point_category))
    print(f"Verified {len(saved)} unique objects and {len(taxonomy)} observed categories.")
