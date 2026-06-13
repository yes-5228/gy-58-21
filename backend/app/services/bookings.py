from datetime import datetime, timezone

from fastapi import HTTPException

from app.data.store import store
from app.models.domain import Booking
from app.schemas import BookingCreate
from app.services import reminders as reminder_service
from app.services.settlement import calculate_payable


def list_bookings() -> list[Booking]:
    return sorted(store.bookings.values(), key=lambda booking: booking.created_at, reverse=True)


def create_booking(payload: BookingCreate) -> Booking:
    slot = store.time_slots.get(payload.slot_id)
    if not slot:
        raise HTTPException(status_code=404, detail="时段不存在")
    if slot.status != "available":
        raise HTTPException(status_code=409, detail="该时段不可预约")

    member = store.members.get(payload.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="会员不存在")

    original, discount, payable = calculate_payable(slot, member)
    booking_id = store.next_booking_id()
    booking = Booking(
        id=booking_id,
        slot_id=slot.id,
        court_id=slot.court_id,
        member_id=member.id,
        member_name=member.name,
        contact_name=payload.contact_name,
        original_amount=original,
        discount_rate=discount,
        payable_amount=payable,
        status="pending",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    store.bookings[booking_id] = booking
    store.time_slots[slot.id] = slot.model_copy(update={"status": "booked"})
    _generate_booking_reminders(booking, slot, "booking_created")
    return booking


def settle_booking(booking_id: int) -> Booking:
    booking = store.bookings.get(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")
    if booking.status == "paid":
        return booking
    paid = booking.model_copy(update={"status": "paid"})
    store.bookings[booking_id] = paid
    return paid


def cancel_booking(booking_id: int) -> Booking:
    booking = store.bookings.get(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="预约不存在")
    canceled = booking.model_copy(update={"status": "canceled"})
    store.bookings[booking_id] = canceled
    slot = store.time_slots.get(booking.slot_id)
    if slot:
        store.time_slots[slot.id] = slot.model_copy(update={"status": "available"})
    _generate_booking_reminders(booking, slot, "booking_canceled")
    return canceled


def _generate_booking_reminders(booking: Booking, slot, event_type: str) -> None:
    event_label = "预约成功" if event_type == "booking_created" else "预约已取消"
    slot_info = f"{slot.label}" if slot else ""
    sms_content = f"【羽毛球预约】{booking.contact_name}{event_label}，时段{slot_info}，金额¥{booking.payable_amount:.2f}"
    in_app_content = f"{booking.contact_name}{event_label}，时段{slot_info}，金额¥{booking.payable_amount:.2f}"
    reminder_service.create_reminder(
        booking_id=booking.id,
        member_id=booking.member_id,
        member_name=booking.member_name,
        contact_name=booking.contact_name,
        event_type=event_type,
        channel="sms",
        content=sms_content,
    )
    reminder_service.create_reminder(
        booking_id=booking.id,
        member_id=booking.member_id,
        member_name=booking.member_name,
        contact_name=booking.contact_name,
        event_type=event_type,
        channel="in_app",
        content=in_app_content,
    )
