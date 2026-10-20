"""Conservative prototype access rules shared by the walking option."""

import pandas as pd

default_walking_types = {
    "footway", "pedestrian", "steps", "path", "residential", "living_street",
    "service", "unclassified", "primary", "primary_link", "secondary",
    "secondary_link", "tertiary", "tertiary_link", "track",
}
fast_road_types = {"motorway", "motorway_link", "trunk", "trunk_link"}
allowed_values = {"yes", "designated", "permissive"}
restricted_values = {"no", "private"}
complex_access_columns = [
    "foot_conditional", "access_conditional", "foot_forward", "foot_backward",
    "oneway_foot", "opening_hours",
]


def classify_walking_access(row):
    highway = row.get("highway")
    foot = row.get("foot")
    access = row.get("access")
    fast_road = highway in fast_road_types or row.get("motorroad") == "yes"

    if highway in {"construction", "proposed"}:
        return "excluded", "inactive_way"
    if any(pd.notna(row.get(column)) for column in complex_access_columns):
        return "review", "conditional_directional_or_timed_access"
    if foot in restricted_values:
        return "excluded", "explicit_foot_restriction"
    if foot in allowed_values:
        if fast_road:
            return "review", "foot_permission_on_fast_road"
        return "included", "explicit_foot_permission"
    if pd.notna(foot):
        return "review", "other_foot_rule"
    if access in restricted_values:
        return "excluded", "general_access_restriction"
    if pd.notna(access) and access not in allowed_values:
        return "review", "limited_or_unknown_general_access"
    if fast_road:
        return "excluded", "fast_road_without_foot_permission"
    if row.get("sidewalk") == "separate":
        return "review", "separately_mapped_sidewalk"
    if highway in default_walking_types:
        return "included", "assumed_access_by_highway_type"
    return "review", "highway_type_needs_review"

def classify_node_access(row):
    foot = row.get("foot")
    access = row.get("access")
    barrier = row.get("barrier")
    allowed = {"yes", "designated", "permissive"}
    restricted = {"no", "private"}

    if any(pd.notna(row.get(key)) for key in ["foot_conditional", "access_conditional", "opening_hours"]):
        return "review", "conditional_or_timed_node_access"
    if row.get("locked") == "yes":
        return "review", "locked_node"
    if foot in restricted:
        return "excluded", "explicit_foot_restriction"
    if foot in allowed:
        if barrier in {"wall", "fence", "hedge", "ditch", "retaining_wall"}:
            return "review", "permission_conflicts_with_physical_barrier"
        return "included", "explicit_foot_permission"
    if pd.notna(foot):
        return "review", "other_foot_rule"
    if access in restricted:
        return "excluded", "general_node_access_restriction"
    if pd.notna(access) and access not in allowed:
        return "review", "limited_or_unknown_node_access"
    if barrier in {"bollard", "cycle_barrier", "entrance", "no"}:
        return "included", "assumed_walkable_barrier"
    if pd.notna(barrier):
        return "review", "barrier_needs_review"
    return "included", "no_node_restriction_detected"

