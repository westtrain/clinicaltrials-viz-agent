from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import VisualizeRequest, VisualizationResponse
from app.llm_planner import plan_query_with_llm
from app.clinicaltrials_client import fetch_studies
from app.transformers import (
    transform_phase_distribution,
    transform_time_trend,
    transform_country_distribution,
    transform_sponsor_drug_network,
    transform_comparison_by_phase,
    transform_intervention_type_distribution,
    filter_studies_by_phase,
)


app = FastAPI(
    title="ClinicalTrials.gov Query-to-Visualization Agent",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/visualize", response_model=VisualizationResponse)
async def visualize(req: VisualizeRequest):
    # plan = plan_query(req)
    plan = plan_query_with_llm(req)
    filters = plan["filters"]

    if plan["intent"] == "unsupported":
        return {
            "visualization": {
                "type": "unsupported",
                "title": "Unsupported query",
                "encoding": {},
                "data": []
            },
            "meta": {
                "source": "clinicaltrials.gov",
                "query_interpretation": plan,
                "study_count": 0,
                "reason": (
                    "This service only supports visualization queries based on "
                    "ClinicalTrials.gov clinical trial data."
                ),
                "supported_query_types": [
                    "time_trend",
                    "phase_distribution",
                    "intervention_type_distribution",
                    "geographic_distribution",
                    "sponsor_drug_network",
                    "comparison"
                ]
            }
        }

    try:
        if plan["intent"] == "comparison":
            if not filters.get("drug_name") or not filters.get("compare_drug_name"):
                raise HTTPException(
                    status_code=400,
                    detail="comparison queries require both drug_name and compare_drug_name"
                )

            drug_name = filters.get("drug_name")
            compare_drug_name = filters.get("compare_drug_name")

            studies_a = await fetch_studies(
                drug_name=drug_name,
                condition=filters.get("condition"),
                sponsor=filters.get("sponsor"),
                country=filters.get("country"),
                overall_status=filters.get("overall_status"),
                max_studies=filters.get("max_studies", req.max_studies),
            )

            studies_b = await fetch_studies(
                drug_name=compare_drug_name,
                condition=filters.get("condition"),
                sponsor=filters.get("sponsor"),
                country=filters.get("country"),
                overall_status=filters.get("overall_status"),
                max_studies=filters.get("max_studies", req.max_studies),
            )

            studies_a = filter_studies_by_phase(
                studies_a,
                trial_phase=filters.get("trial_phase")
            )

            studies_b = filter_studies_by_phase(
                studies_b,
                trial_phase=filters.get("trial_phase")
            )

            visualization = transform_comparison_by_phase(
                studies_a=studies_a,
                studies_b=studies_b,
                label_a=drug_name,
                label_b=compare_drug_name,
                title=f"Phase Comparison: {drug_name} vs {compare_drug_name}"
            )

            return {
                "visualization": visualization,
                "meta": {
                    "source": "clinicaltrials.gov",
                    "query_interpretation": plan,
                    "study_count": {
                        req.drug_name: len(studies_a),
                        req.compare_drug_name: len(studies_b)
                    },
                    "citation_policy": (
                        "Each aggregated datum includes up to 3 compact representative citations "
                        "and full evidence records within the retrieved max_studies dataset."
                    ),
                    "limitations": [
                        "Counts are computed from studies returned by the ClinicalTrials.gov API.",
                        "The current planner uses deterministic rules to reduce hallucination risk.",
                        "Compact citations are capped, while evidence records provide full traceability within the retrieved dataset."
                    ]
                }
            }

        studies = await fetch_studies(
            drug_name=filters.get("drug_name"),
            condition=filters.get("condition"),
            sponsor=filters.get("sponsor"),
            country=filters.get("country"),
            overall_status=filters.get("overall_status"),
            max_studies=filters.get("max_studies", req.max_studies),
        )

        studies = filter_studies_by_phase(
            studies,
            trial_phase=filters.get("trial_phase")
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch data from ClinicalTrials.gov: {str(exc)}"
        )

    if not studies:
        return {
            "visualization": {
                "type": "empty",
                "title": "No matching studies found",
                "encoding": {},
                "data": []
            },
            "meta": {
                "source": "clinicaltrials.gov",
                "query_interpretation": plan,
                "study_count": 0,
                "notes": ["No studies matched the provided filters."]
            }
        }

    intent = plan["intent"]
    entity_label = (
        filters.get("drug_name")
        or filters.get("condition")
        or filters.get("sponsor")
        or filters.get("country")
        or "matching studies"
    )

    if intent == "time_trend":
        visualization = transform_time_trend(
            studies,
            title=f"Trials for {entity_label} by Start Year",
            start_year=req.start_year,
            end_year=req.end_year,
        )

    elif intent == "geographic_distribution":
        visualization = transform_country_distribution(
            studies,
            title=f"Trials for {entity_label} by Country"
        )

    elif intent == "sponsor_drug_network":
        visualization = transform_sponsor_drug_network(
            studies,
            title=f"Sponsor-Drug Network for {entity_label}"
        )

    elif intent == "intervention_type_distribution":
        visualization = transform_intervention_type_distribution(
            studies,
            title=f"Intervention Types for {entity_label} Trials"
        )

    else:
        visualization = transform_phase_distribution(
            studies,
            title=f"Trials for {entity_label} by Phase"
        )

    return {
        "visualization": visualization,
        "meta": {
            "source": "clinicaltrials.gov",
            "query_interpretation": plan,
            "study_count": len(studies),
            "citation_policy": (
                "Each aggregated datum includes up to 3 compact representative citations "
                "and full evidence records within the retrieved max_studies dataset."
            ),
            "limitations": [
                "Counts are computed from studies returned by the ClinicalTrials.gov API.",
                "The current planner uses deterministic rules to reduce hallucination risk.",
                "Compact citations are capped, while evidence records provide full traceability within the retrieved dataset."
            ]
        }
    }