from enum import Enum


class PurchaseListStatus(str, Enum):
    DRAFT = "draft"
    PREPARED = "prepared"
    COMPLETED = "completed"


class InvalidPurchaseListTransition(Exception):
    pass


class PurchaseListWorkflow:
    """Business rules for purchase list status transitions."""

    _transitions = {
        PurchaseListStatus.DRAFT: {
            PurchaseListStatus.PREPARED,
        },
        PurchaseListStatus.PREPARED: {
            PurchaseListStatus.COMPLETED,
        },
        PurchaseListStatus.COMPLETED: set(),
    }

    @classmethod
    def can_transition(
        cls,
        current: str | PurchaseListStatus,
        target: str | PurchaseListStatus,
    ) -> bool:
        current_status = PurchaseListStatus(current)
        target_status = PurchaseListStatus(target)
        return target_status in cls._transitions[current_status]

    @classmethod
    def transition(
        cls,
        current: str | PurchaseListStatus,
        target: str | PurchaseListStatus,
    ) -> str:
        if not cls.can_transition(current, target):
            raise InvalidPurchaseListTransition(
                f"Invalid transition: {current} -> {target}"
            )
        return PurchaseListStatus(target).value
