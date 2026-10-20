"""Build a local walking network around the regional Citiz stations."""

import hashlib
import json
import math
from pathlib import Path

import geopandas as gpd
import networkx as nx
import osmium
import pandas as pd
from pyproj import Transformer
from shapely.geometry import LineString, Point

from walking_rules import classify_node_access, classify_walking_access


ACCESS_KEYS = [
    "barrier", "foot", "access", "locked", "opening_hours", "motorroad",
    "foot:conditional", "access:conditional", "foot:forward", "foot:backward", "oneway:foot",
]


def access_tags(tags):
    """Copy access tags before the temporary OSM object expires."""
    return {key.replace(":", "_"): tags.get(key) for key in ACCESS_KEYS}


def restricted_nodes(path):
    """Keep nodes rejected or left for review by the existing prototype rules."""
    rejected = {}
    processor = osmium.FileProcessor(str(path), osmium.osm.NODE)
    processor = processor.with_filter(osmium.filter.KeyFilter(*ACCESS_KEYS))
    for node in processor:
        status, reason = classify_node_access(access_tags(node.tags))
        if status != "included":
            rejected[str(node.id)] = reason
    return rejected


def network_graph(edges):
    """Represent parallel segments by their minimum length for routing."""
    graph = nx.Graph()
    for edge in edges.itertuples():
        existing = graph.get_edge_data(edge.from_node, edge.to_node)
        if existing is None or edge.length_m < existing["length_m"]:
            graph.add_edge(edge.from_node, edge.to_node, length_m=edge.length_m)
    return graph


def prepare_network(project_directory, margin_m=1300):
    """Reuse or build the network within buffered station neighborhoods."""
    project_directory = Path(project_directory)
    output = project_directory / "regional-data" / "data" / "processed"
    stations_path = output / "citiz_stations_aura.geojson"
    stations = gpd.read_file(stations_path)
    paths = [project_directory / "ign-osm" / "data" / "raw" / "osm" / name for name in [
        "auvergne-261016.osm.pbf", "rhone-alpes-261016.osm.pbf",
    ]]
    rules_path = project_directory / "regional-data" / "walking_rules.py"
    inputs = {
        "version": 1, "margin_m": margin_m,
        "stations_sha256": hashlib.sha256(stations_path.read_bytes()).hexdigest(),
        "rules_sha256": hashlib.sha256(rules_path.read_bytes()).hexdigest(),
        "sources": [{"name": path.name, "size": path.stat().st_size, "modified_ns": path.stat().st_mtime_ns} for path in paths],
    }
    network_path = output / "walking_network.gpkg"
    manifest_path = output / "walking_network_manifest.json"
    if network_path.exists() and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest.get("inputs") == inputs:
            edges = gpd.read_file(network_path, layer="edges")
            return edges, network_graph(edges), manifest

    metric_area = stations.to_crs(epsg=2154).geometry.buffer(margin_m).union_all()
    study_area = gpd.GeoSeries([metric_area], crs="EPSG:2154").to_crs(epsg=4326).iloc[0]
    node_coordinates = {}
    blocked = {}
    records = []
    way_versions = {}
    incomplete_ways = []
    for path in paths:
        print(f"Checking node access in {path.name}...", flush=True)
        blocked.update(restricted_nodes(path))
        print(f"Reading walking ways in {path.name}...", flush=True)
        processor = (
            osmium.FileProcessor(str(path)).with_locations()
            .with_filter(osmium.filter.EntityFilter(osmium.osm.WAY))
            .with_filter(osmium.filter.KeyFilter("highway"))
        )
        for way in processor:
            if way.tags.get("area") == "yes":
                continue
            tags = access_tags(way.tags)
            tags.update(highway=way.tags.get("highway"), sidewalk=way.tags.get("sidewalk"))
            if classify_walking_access(tags)[0] != "included":
                continue
            if way_versions.get(way.id, -1) >= way.version:
                continue
            if len(way.nodes) < 2 or any(not node.location.valid() for node in way.nodes):
                incomplete_ways.append({"source_file": path.name, "osm_way_id": str(way.id)})
                continue
            coordinates = [(node.lon, node.lat) for node in way.nodes]
            if not LineString(coordinates).intersects(study_area):
                continue
            way_versions[way.id] = way.version
            way_nodes = list(way.nodes)
            for index, (start, end) in enumerate(zip(way_nodes, way_nodes[1:])):
                if start.ref == end.ref:
                    continue
                geometry = LineString([(start.lon, start.lat), (end.lon, end.lat)])
                if not geometry.intersects(study_area):
                    continue
                start_id, end_id = str(start.ref), str(end.ref)
                node_coordinates[start_id] = (start.lon, start.lat)
                node_coordinates[end_id] = (end.lon, end.lat)
                records.append({
                    "edge_id": f"{way.id}:{index}", "from_node": start_id,
                    "to_node": end_id, "osm_way_id": str(way.id), "osm_version": way.version,
                })
    table = pd.DataFrame(records, columns=["edge_id", "from_node", "to_node", "osm_way_id", "osm_version"])
    table = table.sort_values("osm_version").drop_duplicates("edge_id", keep="last")
    latest_versions = table.groupby("osm_way_id")["osm_version"].transform("max")
    table = table.loc[table["osm_version"].eq(latest_versions)].copy()
    table = table.loc[~table["from_node"].isin(blocked) & ~table["to_node"].isin(blocked)].copy()
    used_nodes = sorted(set(table["from_node"]) | set(table["to_node"]))
    transformer = Transformer.from_crs(4326, 2154, always_xy=True)
    longitudes, latitudes = zip(*(node_coordinates[node_id] for node_id in used_nodes))
    x_coordinates, y_coordinates = transformer.transform(longitudes, latitudes)
    positions = dict(zip(used_nodes, zip(x_coordinates, y_coordinates)))
    geometries = [LineString([positions[start], positions[end]]) for start, end in zip(table["from_node"], table["to_node"])]
    edges = gpd.GeoDataFrame(table, geometry=geometries, crs="EPSG:2154")
    edges["length_m"] = edges.geometry.length
    edges = edges.loc[edges["length_m"] > 0].reset_index(drop=True)
    assert edges["edge_id"].is_unique and edges.geometry.is_valid.all()
    edges.to_file(network_path, layer="edges", driver="GPKG")
    pd.DataFrame(incomplete_ways, columns=["source_file", "osm_way_id"]).to_csv(output / "walking_network_incomplete_ways.csv", index=False)
    pd.DataFrame(list(blocked.items()), columns=["osm_node_id", "reason"]).to_csv(output / "walking_blocked_nodes.csv", index=False)
    graph = network_graph(edges)
    manifest = {"inputs": inputs, "edge_count": len(edges), "node_count": graph.number_of_nodes(), "incomplete_way_count": len(incomplete_ways), "blocked_source_node_count": len(blocked), "status": "prototype_undirected_node_filtered_relations_not_handled"}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return edges, graph, manifest


def snap_points_to_network(points, edges, max_distance_m=100):
    """Attach point geometries to their nearest network node, within a safe limit."""
    coordinates = {}
    for edge in edges.itertuples():
        coordinates.setdefault(edge.from_node, (edge.geometry.coords[0][0], edge.geometry.coords[0][1]))
        coordinates.setdefault(edge.to_node, (edge.geometry.coords[-1][0], edge.geometry.coords[-1][1]))
    node_ids = list(coordinates)
    node_geometries = gpd.GeoSeries(
        [Point(coordinates[node_id]) for node_id in node_ids], crs=edges.crs
    )
    node_index = node_geometries.sindex
    snapped = []
    for point in points:
        candidate_indexes = node_index.query(point.buffer(max_distance_m), predicate="intersects")
        if len(candidate_indexes) == 0:
            snapped.append((None, None))
            continue
        candidates = node_geometries.iloc[candidate_indexes]
        distances = candidates.distance(point)
        closest_index = distances.idxmin()
        closest_distance = float(distances.loc[closest_index])
        snapped.append((node_ids[closest_index], closest_distance))
    return snapped


def reachable_graph(graph, station_node, radius_m):
    """Return shortest distances only in the station's useful network area."""
    if station_node is None or station_node not in graph:
        return {}
    return nx.single_source_dijkstra_path_length(
        graph, station_node, cutoff=radius_m, weight="length_m"
    )
