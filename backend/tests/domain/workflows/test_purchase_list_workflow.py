from app.domain.workflows.purchase_list import (
    InvalidPurchaseListTransition,
    PurchaseListWorkflow,
)


def test_purchase_list_allowed_transition():
    assert PurchaseListWorkflow.can_transition("draft", "prepared")


def test_purchase_list_forbidden_transition():
    assert not PurchaseListWorkflow.can_transition("completed", "draft")


def test_purchase_list_transition_raises_error():
    try:
        PurchaseListWorkflow.transition("completed", "draft")
        assert False
    except InvalidPurchaseListTransition:
        assert True
