import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from openai import OpenAI

from app.schemas import VisualizeRequest
from app.planner import plan_query


load_dotenv()


ALLOWED_INTENTS = {
    "time_trend",
    "phase_distribution",
    "geographic_distribution",
    "sponsor_drug_network",
    "comparison",
    "intervention_type_distribution",
    "unsupported",
}


ALLOWED_VISUALIZATION_TYPES = {
    "time_series",
    "bar_chart",
    "network_graph",
    "grouped_bar_chart",
    "unsupported",
}


def normalize_plan(plan: Dict[str, Any], req: VisualizeRequest) -> Dict[str, Any]:
    intent = plan.get("intent")
    visualization_type = plan.get("visualization_type")

    if intent not in ALLOWED_INTENTS:
        raise ValueError(f"Invalid intent from LLM: {intent}")

    intent_to_visualization_type = {
        "time_trend": "time_series",
        "phase_distribution": "bar_chart",
        "geographic_distribution": "bar_chart",
        "sponsor_drug_network": "network_graph",
        "comparison": "grouped_bar_chart",
        "intervention_type_distribution": "bar_chart",
        "unsupported": "unsupported",
    }

    visualization_type = intent_to_visualization_type[intent]

    filters = plan.get("filters", {})

    return {
        "intent": intent,
        "visualization_type": visualization_type,
        "filters": {
            "drug_name": filters.get("drug_name") or req.drug_name,
            "compare_drug_name": filters.get("compare_drug_name") or req.compare_drug_name,
            "condition": filters.get("condition") or req.condition,
            "trial_phase": filters.get("trial_phase") or req.trial_phase,
            "sponsor": filters.get("sponsor") or req.sponsor,
            "country": filters.get("country") or req.country,
            "start_year": filters.get("start_year") or req.start_year,
            "end_year": filters.get("end_year") or req.end_year,
            "overall_status": filters.get("overall_status") or req.overall_status,
            "max_studies": req.max_studies,
        },
        "planner": "llm"
    }


def plan_query_with_llm(req: VisualizeRequest) -> Dict[str, Any]:
    preliminary_plan = plan_query(req)

    if preliminary_plan["intent"] == "unsupported":
        preliminary_plan["planner"] = "rule_based_scope_guard"
        return preliminary_plan
    
    if not req.use_llm:
        fallback_plan = plan_query(req)
        fallback_plan["planner"] = "rule_based_forced"
        return fallback_plan

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        fallback_plan = plan_query(req)
        fallback_plan["planner"] = "rule_based_no_api_key"
        return fallback_plan

    client = OpenAI(api_key=api_key)

    system_prompt = """
You are a query planning assistant for a ClinicalTrials.gov visualization backend.

Your job is to convert a user's clinical trial question into a strict JSON plan.

You must only choose one of these intents:
- time_trend
- phase_distribution
- geographic_distribution
- sponsor_drug_network
- comparison
- intervention_type_distribution
- unsupported

You must only choose one of these visualization_type values:
- time_series
- bar_chart
- network_graph
- grouped_bar_chart

Rules:
- Use time_trend for questions about yearly changes, trends, or changes over time.
- Use phase_distribution for questions about trial phases or phase distribution.
- Use geographic_distribution for questions about countries, locations, or recruiting trials by country.
- Use sponsor_drug_network for questions about sponsor-drug relationships or networks.
- Use comparison for comparing two drugs.
- Use intervention_type_distribution for questions about common intervention types or intervention type distribution.
- Use unsupported when the user question is not about clinical trials, drugs, diseases, study phases, sponsors, interventions, recruitment status, or ClinicalTrials.gov data.

Important:
- Do not invent chart values.
- Do not generate trial counts.
- Do not generate citations.
- Only extract query intent and filters.
- Prefer structured fields supplied by the user.
- Return JSON only.
"""

    user_payload = {
        "query": req.query,
        "structured_fields": {
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
        },
        "expected_json_shape": {
            "intent": "time_trend | phase_distribution | geographic_distribution | sponsor_drug_network | comparison",
            "visualization_type": "time_series | bar_chart | network_graph | grouped_bar_chart",
            "filters": {
                "drug_name": "string or null",
                "compare_drug_name": "string or null",
                "condition": "string or null",
                "trial_phase": "string or null",
                "sponsor": "string or null",
                "country": "string or null",
                "start_year": "integer or null",
                "end_year": "integer or null",
                "overall_status": "string or null"
            }
        }
    }

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload)}
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty LLM response")

        raw_plan = json.loads(content)
        return normalize_plan(raw_plan, req)

    except Exception:
        fallback_plan = plan_query(req)
        fallback_plan["planner"] = "rule_based_fallback"
        return fallback_plan