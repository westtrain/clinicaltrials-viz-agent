from app.transformers import (
    transform_phase_distribution,
    transform_intervention_type_distribution,
    transform_sponsor_drug_network,
)


def make_study(
    nct_id: str,
    title: str,
    phases=None,
    interventions=None,
    sponsor="Example Sponsor"
):
    return {
        "protocolSection": {
            "identificationModule": {
                "nctId": nct_id,
                "briefTitle": title
            },
            "designModule": {
                "phases": phases or []
            },
            "armsInterventionsModule": {
                "interventions": interventions or []
            },
            "sponsorCollaboratorsModule": {
                "leadSponsor": {
                    "name": sponsor
                }
            }
        }
    }


def test_phase_distribution_counts_and_evidence():
    studies = [
        make_study("NCT001", "Study 1", phases=["PHASE3"]),
        make_study("NCT002", "Study 2", phases=["PHASE3"]),
        make_study("NCT003", "Study 3", phases=["PHASE2"]),
    ]

    result = transform_phase_distribution(studies, "Trials by Phase")
    data_by_phase = {row["phase"]: row for row in result["data"]}

    assert result["type"] == "bar_chart"

    assert data_by_phase["PHASE3"]["trial_count"] == 2
    assert data_by_phase["PHASE3"]["evidence"]["supporting_record_count"] == 2
    assert len(data_by_phase["PHASE3"]["evidence"]["records"]) == 2

    assert data_by_phase["PHASE2"]["trial_count"] == 1
    assert data_by_phase["PHASE2"]["evidence"]["supporting_record_count"] == 1


def test_intervention_type_distribution_counts_and_evidence():
    studies = [
        make_study(
            "NCT001",
            "Study 1",
            interventions=[
                {"type": "DRUG", "name": "Drug A"},
                {"type": "BIOLOGICAL", "name": "Bio A"},
            ],
        ),
        make_study(
            "NCT002",
            "Study 2",
            interventions=[
                {"type": "DRUG", "name": "Drug B"},
            ],
        ),
    ]

    result = transform_intervention_type_distribution(
        studies,
        "Intervention Types"
    )

    data_by_type = {row["intervention_type"]: row for row in result["data"]}

    assert result["type"] == "bar_chart"

    assert data_by_type["DRUG"]["trial_count"] == 2
    assert data_by_type["DRUG"]["evidence"]["supporting_record_count"] == 2

    assert data_by_type["BIOLOGICAL"]["trial_count"] == 1
    assert data_by_type["BIOLOGICAL"]["evidence"]["supporting_record_count"] == 1


def test_sponsor_drug_network_weight_and_evidence():
    studies = [
        make_study(
            "NCT001",
            "Study 1",
            interventions=[
                {"type": "DRUG", "name": "Pembrolizumab"}
            ],
            sponsor="Merck"
        ),
        make_study(
            "NCT002",
            "Study 2",
            interventions=[
                {"type": "DRUG", "name": "Pembrolizumab"}
            ],
            sponsor="Merck"
        ),
    ]

    result = transform_sponsor_drug_network(
        studies,
        "Sponsor Drug Network"
    )

    edges = result["data"]["edges"]

    assert result["type"] == "network_graph"
    assert len(edges) == 1

    edge = edges[0]

    assert edge["source"] == "sponsor::Merck"
    assert edge["target"] == "drug::Pembrolizumab"
    assert edge["weight"] == 2
    assert edge["evidence"]["supporting_record_count"] == 2
    assert len(edge["evidence"]["records"]) == 2