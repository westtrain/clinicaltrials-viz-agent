from collections import defaultdict
from typing import Any, Dict, List, Optional

from app.citations import get_nested, build_citation, build_evidence_record, build_evidence


def get_phases(study: Dict[str, Any]) -> List[str]:
    phases = get_nested(study, "protocolSection.designModule.phases", [])

    if not phases:
        return ["Not Available"]

    return phases

def normalize_phase(value: str) -> str:
    return (
        value
        .strip()
        .upper()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )


def filter_studies_by_phase(
    studies: List[Dict[str, Any]],
    trial_phase: Optional[str] = None
) -> List[Dict[str, Any]]:
    if not trial_phase:
        return studies

    normalized_target = normalize_phase(trial_phase)

    filtered_studies = []

    for study in studies:
        phases = get_phases(study)
        normalized_phases = [normalize_phase(phase) for phase in phases]

        if normalized_target in normalized_phases:
            filtered_studies.append(study)

    return filtered_studies

def get_start_year(study: Dict[str, Any]) -> Optional[int]:
    date_value = get_nested(
        study,
        "protocolSection.statusModule.startDateStruct.date"
    )

    if not date_value:
        return None

    try:
        return int(str(date_value)[:4])
    except ValueError:
        return None


def get_interventions(study: Dict[str, Any]) -> List[Dict[str, Any]]:
    return get_nested(
        study,
        "protocolSection.armsInterventionsModule.interventions",
        []
    ) or []

def transform_intervention_type_distribution(
    studies: List[Dict[str, Any]],
    title: str
) -> Dict[str, Any]:
    buckets = defaultdict(lambda: {
        "trial_count": 0,
        "citations": [],
        "evidence_records": []
    })

    for study in studies:
        intervention_types = set()

        for intervention in get_interventions(study):
            intervention_type = intervention.get("type")

            if intervention_type:
                intervention_types.add(intervention_type)

        if not intervention_types:
            intervention_types.add("Not Available")

        for intervention_type in intervention_types:
            buckets[intervention_type]["trial_count"] += 1

            buckets[intervention_type]["evidence_records"].append(
                build_evidence_record(
                    study,
                    "protocolSection.armsInterventionsModule.interventions.type",
                    value=intervention_type
                )
            )

            if len(buckets[intervention_type]["citations"]) < 3:
                buckets[intervention_type]["citations"].append(
                    build_citation(
                        study,
                        "protocolSection.armsInterventionsModule.interventions.type",
                        excerpt=intervention_type
                    )
                )

    data = sorted(
        [
            {
                "intervention_type": intervention_type,
                "trial_count": value["trial_count"],
                "citations": value["citations"],
                "evidence": build_evidence(value["evidence_records"])
            }
            for intervention_type, value in buckets.items()
        ],
        key=lambda row: row["trial_count"],
        reverse=True
    )

    return {
        "type": "bar_chart",
        "title": title,
        "encoding": {
            "x": {"field": "intervention_type", "type": "nominal"},
            "y": {"field": "trial_count", "type": "quantitative"}
        },
        "data": data
    }

def get_drug_names(study: Dict[str, Any]) -> List[str]:
    names = []

    for intervention in get_interventions(study):
        intervention_type = intervention.get("type")
        name = intervention.get("name")

        if intervention_type in ["DRUG", "BIOLOGICAL"] and name:
            names.append(name)

    return list(dict.fromkeys(names))


def get_lead_sponsor(study: Dict[str, Any]) -> str:
    return get_nested(
        study,
        "protocolSection.sponsorCollaboratorsModule.leadSponsor.name",
        "Unknown Sponsor"
    )


def get_countries(study: Dict[str, Any]) -> List[str]:
    locations = get_nested(
        study,
        "protocolSection.contactsLocationsModule.locations",
        []
    ) or []

    countries = []

    for location in locations:
        country = location.get("country")
        if country:
            countries.append(country)

    return list(set(countries))


def transform_phase_distribution(
    studies: List[Dict[str, Any]],
    title: str
) -> Dict[str, Any]:
    buckets = defaultdict(lambda: {
        "trial_count": 0,
        "citations": [],
        "evidence_records": []
    })

    for study in studies:
        for phase in get_phases(study):
            buckets[phase]["trial_count"] += 1

            buckets[phase]["evidence_records"].append(
                build_evidence_record(
                    study,
                    "protocolSection.designModule.phases",
                    value=str(phase)
                )
            )

            if len(buckets[phase]["citations"]) < 3:
                buckets[phase]["citations"].append(
                    build_citation(
                        study,
                        "protocolSection.designModule.phases",
                        excerpt=str(phase)
                    )
                )

    data = [
        {
            "phase": phase,
            "trial_count": value["trial_count"],
            "citations": value["citations"],
            "evidence": build_evidence(value["evidence_records"])
        }
        for phase, value in sorted(buckets.items())
    ]

    return {
        "type": "bar_chart",
        "title": title,
        "encoding": {
            "x": {"field": "phase", "type": "nominal"},
            "y": {"field": "trial_count", "type": "quantitative"}
        },
        "data": data
    }

def transform_time_trend(
    studies: List[Dict[str, Any]],
    title: str,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None
) -> Dict[str, Any]:
    buckets = defaultdict(lambda: {
        "trial_count": 0,
        "citations": [],
        "evidence_records": []
    })

    for study in studies:
        year = get_start_year(study)

        if not year:
            continue

        if start_year and year < start_year:
            continue

        if end_year and year > end_year:
            continue

        buckets[year]["trial_count"] += 1

        buckets[year]["evidence_records"].append(
            build_evidence_record(
                study,
                "protocolSection.statusModule.startDateStruct.date",
                value=str(year)
            )
        )

        if len(buckets[year]["citations"]) < 3:
            buckets[year]["citations"].append(
                build_citation(
                    study,
                    "protocolSection.statusModule.startDateStruct.date",
                    excerpt=str(year)
                )
            )

    data = [
        {
            "year": year,
            "trial_count": value["trial_count"],
            "citations": value["citations"],
            "evidence": build_evidence(value["evidence_records"])
        }
        for year, value in sorted(buckets.items())
    ]

    return {
        "type": "time_series",
        "title": title,
        "encoding": {
            "x": {"field": "year", "type": "temporal"},
            "y": {"field": "trial_count", "type": "quantitative"}
        },
        "data": data
    }

def transform_country_distribution(
    studies: List[Dict[str, Any]],
    title: str
) -> Dict[str, Any]:
    buckets = defaultdict(lambda: {
        "trial_count": 0,
        "citations": [],
        "evidence_records": []
    })

    for study in studies:
        for country in get_countries(study):
            buckets[country]["trial_count"] += 1

            buckets[country]["evidence_records"].append(
                build_evidence_record(
                    study,
                    "protocolSection.contactsLocationsModule.locations.country",
                    value=country
                )
            )

            if len(buckets[country]["citations"]) < 3:
                buckets[country]["citations"].append(
                    build_citation(
                        study,
                        "protocolSection.contactsLocationsModule.locations.country",
                        excerpt=country
                    )
                )

    data = sorted(
        [
            {
                "country": country,
                "trial_count": value["trial_count"],
                "citations": value["citations"],
                "evidence": build_evidence(value["evidence_records"])
            }
            for country, value in buckets.items()
        ],
        key=lambda row: row["trial_count"],
        reverse=True
    )[:20]

    return {
        "type": "bar_chart",
        "title": title,
        "encoding": {
            "x": {"field": "country", "type": "nominal"},
            "y": {"field": "trial_count", "type": "quantitative"}
        },
        "data": data
    }

def transform_sponsor_drug_network(
    studies: List[Dict[str, Any]],
    title: str
) -> Dict[str, Any]:
    node_map: Dict[str, Dict[str, Any]] = {}
    edge_map = defaultdict(lambda: {
        "weight": 0,
        "citations": [],
        "evidence_records": []
    })

    for study in studies:
        sponsor = get_lead_sponsor(study)
        drugs = get_drug_names(study)

        if not sponsor or not drugs:
            continue

        sponsor_id = f"sponsor::{sponsor}"

        node_map[sponsor_id] = {
            "id": sponsor_id,
            "label": sponsor,
            "type": "sponsor"
        }

        for drug in drugs:
            drug_id = f"drug::{drug}"

            node_map[drug_id] = {
                "id": drug_id,
                "label": drug,
                "type": "drug"
            }

            edge_key = (sponsor_id, drug_id)
            edge_map[edge_key]["weight"] += 1

            edge_map[edge_key]["evidence_records"].append(
                build_evidence_record(
                    study,
                    "protocolSection.sponsorCollaboratorsModule.leadSponsor.name + protocolSection.armsInterventionsModule.interventions.name",
                    value=f"{sponsor} -> {drug}"
                )
            )

            if len(edge_map[edge_key]["citations"]) < 3:
                edge_map[edge_key]["citations"].append(
                    build_citation(
                        study,
                        "protocolSection.sponsorCollaboratorsModule.leadSponsor.name + protocolSection.armsInterventionsModule.interventions.name",
                        excerpt=f"{sponsor} -> {drug}"
                    )
                )

    edges = [
        {
            "source": source,
            "target": target,
            "weight": value["weight"],
            "citations": value["citations"],
            "evidence": build_evidence(value["evidence_records"])
        }
        for (source, target), value in edge_map.items()
    ]

    edges = sorted(edges, key=lambda edge: edge["weight"], reverse=True)[:50]

    used_node_ids = set()

    for edge in edges:
        used_node_ids.add(edge["source"])
        used_node_ids.add(edge["target"])

    nodes = [
        node
        for node_id, node in node_map.items()
        if node_id in used_node_ids
    ]

    return {
        "type": "network_graph",
        "title": title,
        "encoding": {
            "nodes": {
                "id": "id",
                "label": "label",
                "group": "type"
            },
            "edges": {
                "source": "source",
                "target": "target",
                "weight": "weight"
            }
        },
        "data": {
            "nodes": nodes,
            "edges": edges
        }
    }

def transform_comparison_by_phase(
    studies_a: List[Dict[str, Any]],
    studies_b: List[Dict[str, Any]],
    label_a: str,
    label_b: str,
    title: str
) -> Dict[str, Any]:
    buckets = defaultdict(lambda: {
        label_a: {
            "trial_count": 0,
            "citations": [],
            "evidence_records": []
        },
        label_b: {
            "trial_count": 0,
            "citations": [],
            "evidence_records": []
        }
    })

    for study in studies_a:
        for phase in get_phases(study):
            buckets[phase][label_a]["trial_count"] += 1

            buckets[phase][label_a]["evidence_records"].append(
                build_evidence_record(
                    study,
                    "protocolSection.designModule.phases",
                    value=f"{label_a}: {phase}"
                )
            )

            if len(buckets[phase][label_a]["citations"]) < 3:
                buckets[phase][label_a]["citations"].append(
                    build_citation(
                        study,
                        "protocolSection.designModule.phases",
                        excerpt=f"{label_a}: {phase}"
                    )
                )

    for study in studies_b:
        for phase in get_phases(study):
            buckets[phase][label_b]["trial_count"] += 1

            buckets[phase][label_b]["evidence_records"].append(
                build_evidence_record(
                    study,
                    "protocolSection.designModule.phases",
                    value=f"{label_b}: {phase}"
                )
            )

            if len(buckets[phase][label_b]["citations"]) < 3:
                buckets[phase][label_b]["citations"].append(
                    build_citation(
                        study,
                        "protocolSection.designModule.phases",
                        excerpt=f"{label_b}: {phase}"
                    )
                )

    data = []

    for phase in sorted(buckets.keys()):
        data.append({
            "phase": phase,
            "series": label_a,
            "trial_count": buckets[phase][label_a]["trial_count"],
            "citations": buckets[phase][label_a]["citations"],
            "evidence": build_evidence(buckets[phase][label_a]["evidence_records"])
        })

        data.append({
            "phase": phase,
            "series": label_b,
            "trial_count": buckets[phase][label_b]["trial_count"],
            "citations": buckets[phase][label_b]["citations"],
            "evidence": build_evidence(buckets[phase][label_b]["evidence_records"])
        })

    return {
        "type": "grouped_bar_chart",
        "title": title,
        "encoding": {
            "x": {"field": "phase", "type": "nominal"},
            "y": {"field": "trial_count", "type": "quantitative"},
            "series": {"field": "series", "type": "nominal"}
        },
        "data": data
    }