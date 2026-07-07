from app.domain.workflows.purchase_checklist import (
    PurchaseChecklistWorkflow,
)


def test_purchase_checklist_allowed_transition():
    assert PurchaseChecklistWorkflow.can_transition("draft", "in_progress")


def test_purchase_checklist_completed_transition():
    assert PurchaseChecklistWorkflow.can_transition("in_progress", "completed")


def test_purchase_checklist_direct_completion_from_draft():
    assert PurchaseChecklistWorkflow.can_transition("draft", "completed")
