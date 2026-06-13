from fastapi import APIRouter

from app.models.domain import Reminder
from app.services import reminders as reminder_service

router = APIRouter(tags=["reminders"])


@router.get("/reminders", response_model=list[Reminder])
def list_reminders() -> list[Reminder]:
    return reminder_service.list_reminders()
