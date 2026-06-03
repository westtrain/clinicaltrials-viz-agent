from app.planner import plan_query
from app.schemas import VisualizeRequest


def test_rule_based_planner_phase_distribution():
    req = VisualizeRequest(
        query="How are lung cancer trials distributed across phases?",
        condition="Lung Cancer",
        use_llm=False,
        max_studies=10
    )

    plan = plan_query(req)

    assert plan["intent"] == "phase_distribution"
    assert plan["visualization_type"] == "bar_chart"
    assert plan["filters"]["condition"] == "Lung Cancer"


def test_rule_based_planner_intervention_type_distribution():
    req = VisualizeRequest(
        query="What are the most common intervention types in lung cancer trials?",
        condition="Lung Cancer",
        use_llm=False,
        max_studies=10
    )

    plan = plan_query(req)

    assert plan["intent"] == "intervention_type_distribution"
    assert plan["visualization_type"] == "bar_chart"
    assert plan["filters"]["condition"] == "Lung Cancer"


def test_rule_based_planner_comparison():
    req = VisualizeRequest(
        query="Compare trial phases for Pembrolizumab versus Nivolumab.",
        drug_name="Pembrolizumab",
        compare_drug_name="Nivolumab",
        use_llm=False,
        max_studies=10
    )

    plan = plan_query(req)

    assert plan["intent"] == "comparison"
    assert plan["visualization_type"] == "grouped_bar_chart"
    assert plan["filters"]["drug_name"] == "Pembrolizumab"
    assert plan["filters"]["compare_drug_name"] == "Nivolumab"


def test_rule_based_planner_unsupported_query():
    req = VisualizeRequest(
        query="Show me the population statistics of South Korea.",
        use_llm=False,
        max_studies=10
    )

    plan = plan_query(req)

    assert plan["intent"] == "unsupported"
    assert plan["visualization_type"] == "unsupported"