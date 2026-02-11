from ai_decision_router.classifier import classify_task


def test_classifier_categories() -> None:
    assert classify_task("Debug this python function") == "code"
    assert classify_task("Prove this logic step by step") == "reasoning"
    assert classify_task("Run SQL query on table data") == "data"
    assert classify_task("Rewrite this essay with better tone") == "writing"
    assert classify_task("Hello there") == "chat/general"
