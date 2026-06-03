from typing import Any, Dict
from app.schemas import VisualizeRequest


def plan_query(req: VisualizeRequest) -> Dict[str, Any]:
    query = req.query.lower()

    clinical_trial_keywords = [
        "clinical trial",
        "clinical trials",
        "trial",
        "trials",
        "study",
        "studies",
        "drug",
        "drugs",
        "condition",
        "disease",
        "phase",
        "phases",
        "sponsor",
        "intervention",
        "interventions",
        "recruiting",
        "recruitment",
        "country",
        "countries",
        "location",
        "locations",
        "nct",
    ]

    has_structured_filter = any([
        req.drug_name,
        req.compare_drug_name,
        req.condition,
        req.trial_phase,
        req.sponsor,
        req.country,
        req.overall_status,
    ])

    is_potential_clinical_trials_query = (
        any(keyword in query for keyword in clinical_trial_keywords)
        or has_structured_filter
    )

    if not is_potential_clinical_trials_query:
        return {
            "intent": "unsupported",
            "visualization_type": "unsupported",
            "filters": {
                "drug_name": req.drug_name,
                "compare_drug_name": req.compare_drug_name,
                "condition": req.condition,
                "trial_phase": req.trial_phase,
                "sponsor": req.sponsor,
                "country": req.country,
                "start_year": req.start_year,
                "end_year": req.end_year,
                "overall_status": req.overall_status,
                "max_studies": req.max_studies,
            }
        }

    if req.compare_drug_name or "compare" in query or " vs " in query or " versus " in query:
        intent = "comparison"
        visualization_type = "grouped_bar_chart"

    elif any(keyword in query for keyword in ["over time", "per year", "yearly", "trend", "changed", "each year"]):
        intent = "time_trend"
        visualization_type = "time_series"

    elif any(keyword in query for keyword in ["country", "countries", "location", "locations", "where"]):
        intent = "geographic_distribution"
        visualization_type = "bar_chart"

    elif any(keyword in query for keyword in ["network", "relationship", "relationships", "co-occur", "cooccur", "sponsor"]):
        intent = "sponsor_drug_network"
        visualization_type = "network_graph"

    elif any(keyword in query for keyword in ["intervention type", "intervention types", "common intervention", "most common intervention"]):
        intent = "intervention_type_distribution"
        visualization_type = "bar_chart"

    elif any(keyword in query for keyword in ["phase", "phases", "distributed", "distribution"]):
        intent = "phase_distribution"
        visualization_type = "bar_chart"

    else:
        intent = "phase_distribution"
        visualization_type = "bar_chart"

    return {
        "intent": intent,
        "visualization_type": visualization_type,
        "filters": {
            "drug_name": req.drug_name,
            "compare_drug_name": req.compare_drug_name,
            "condition": req.condition,
            "trial_phase": req.trial_phase,
            "sponsor": req.sponsor,
            "country": req.country,
            "start_year": req.start_year,
            "end_year": req.end_year,
            "overall_status": req.overall_status,
            "max_studies": req.max_studies,
        }
    }