from datetime import datetime, timezone

from app.data.store import store
from app.models.domain import Reminder


def list_reminders() -> list[Reminder]:
    return sorted(store.reminders.values(), key=lambda r: r.created_at, reverse=True)


def create_reminder(
    booking_id: int,
    member_id: int,
    member_name: str,
    contact_name: str,
    event_type: str,
    channel: str,
    content: str,
) -> Reminder:
    reminder_id = store.next_reminder_id()
    sms_status = "sent" if channel == "sms" and _simulate_send(member_id, channel, content) else "pending"
    reminder = Reminder(
        id=reminder_id,
        booking_id=booking_id,
        member_id=member_id,
        member_name=member_name,
        contact_name=contact_name,
        event_type=event_type,
        channel=channel,
        status=sms_status,
        content=content,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    store.reminders[reminder_id] = reminder
    return reminder


def _simulate_send(member_id: int, channel: str, content: str) -> bool:
    member = store.members.get(member_id)
    if channel == "sms":
        return bool(member and member.phone)
    return True
