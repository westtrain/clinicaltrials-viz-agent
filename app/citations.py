from typing import Any, Dict, Optional


def get_nested(data: Dict[str, Any], path: str, default=None):
    current: Any = data

    for part in path.split("."):
        if not isinstance(current, dict):
            return default

        current = current.get(part)

        if current is None:
            return default

    return current


def get_nct_id(study: Dict[str, Any]) -> str:
    return get_nested(
        study,
        "protocolSection.identificationModule.nctId",
        "UNKNOWN"
    )


def get_brief_title(study: Dict[str, Any]) -> str:
    return get_nested(
        study,
        "protocolSection.identificationModule.briefTitle",
        ""
    )


def build_citation(
    study: Dict[str, Any],
    field: str,
    excerpt: Optional[str] = None
) -> Dict[str, str]:
    return {
        "nct_id": get_nct_id(study),
        "field": field,
        "excerpt": excerpt or get_brief_title(study)
    }

def build_evidence_record(
    study: Dict[str, Any],
    field: str,
    value: Optional[str] = None
) -> Dict[str, str]:
    return {
        "nct_id": get_nct_id(study),
        "field": field,
        "value": value or "",
        "brief_title": get_brief_title(study)
    }

def build_evidence(records: list[Dict[str, str]]) -> Dict[str, Any]:
    return {
        "supporting_record_count": len(records),
        "records": records
    }