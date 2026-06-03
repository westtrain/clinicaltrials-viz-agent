import pytest

from app.clinicaltrials_client import fetch_studies
from app.transformers import transform_time_trend


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fetch_studies_from_clinicaltrials_api():
    studies = await fetch_studies(
        drug_name="Pembrolizumab",
        max_studies=3
    )

    assert isinstance(studies, list)
    assert len(studies) > 0

    first_study = studies[0]

    assert "protocolSection" in first_study

    identification = first_study["protocolSection"].get(
        "identificationModule",
        {}
    )

    assert "nctId" in identification


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_data_can_be_transformed_to_time_series():
    studies = await fetch_studies(
        drug_name="Pembrolizumab",
        max_studies=10
    )

    result = transform_time_trend(
        studies,
        title="Trials for Pembrolizumab by Start Year",
        start_year=2015
    )

    assert result["type"] == "time_series"
    assert "data" in result
    assert isinstance(result["data"], list)

    for row in result["data"]:
        assert "year" in row
        assert "trial_count" in row
        assert "evidence" in row
        assert row["trial_count"] == row["evidence"]["supporting_record_count"]