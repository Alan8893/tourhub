from enum import Enum


class PurchaseChecklistStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class InvalidPurchaseChecklistTransition(Exception):
    pass


class PurchaseChecklistWorkflow:
    """Business rules for purchase checklist status transitions."""

    _transitions = {
        PurchaseChecklistStatus.DRAFT: {
            PurchaseChecklistStatus.IN_PROGRESS,
            PurchaseChecklistStatus.COMPLETED,
        },
        PurchaseChecklistStatus.IN_PROGRESS: {
            PurchaseChecklistStatus.COMPLETED,
            PurchaseChecklistStatus.DRAFT,
        },
        PurchaseChecklistStatus.COMPLETED: {
            PurchaseChecklistStatus.IN_PROGRESS,
        },
    }

    @classmethod
    def can_transition(
        cls,
        current: str | PurchaseChecklistStatus,
        target: str | PurchaseChecklistStatus,
    ) -> bool:
        current_status = PurchaseChecklistStatus(current)
        target_status = PurchaseChecklistStatus(target)
        return target_status in cls._transitions[current_status]

    @classmethod
    def transition(
        cls,
        current: str | PurchaseChecklistStatus,
        target: str | PurchaseChecklistStatus,
    ) -> str:
        if not cls.can_transition(current, target):
            raise InvalidPurchaseChecklistTransition(
                f"Invalid transition: {current} -> {target}"
            )
        return PurchaseChecklistStatus(target).value
