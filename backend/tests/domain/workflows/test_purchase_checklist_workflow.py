from app.domain.workflows.purchase_checklist import (
    InvalidPurchaseChecklistTransition,
    PurchaseChecklistWorkflow,
)


def test_purchase_checklist_allowed_transition():
    assert PurchaseChecklistWorkflow.can_transition("draft", "in_progress")


def test_purchase_checklist_completed_transition():
    assert PurchaseChecklistWorkflow.can_transition("in_progress", "completed")


def test_purchase_checklist_forbidden_transition():
    try:
        PurchaseChecklistWorkflow.transition("draft", "completed")
        assert False
    except InvalidPurchaseChecklistTransition:
        assert True
