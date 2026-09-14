from typing import List, Dict, Any
from datetime import datetime, timezone
import logging

from src.domain.models import Dispatch, Volunteer, DonationAlert
from src.ports.driven.notification_port import NotificationPort

logger = logging.getLogger("PantryPulseNotifier")

class MockNotificationAdapter(NotificationPort):
    def __init__(self):
        self._sent_messages: List[Dict[str, Any]] = []

    def notify_volunteer_dispatch(self, volunteer: Volunteer, dispatch: Dispatch, donation: DonationAlert) -> bool:
        sms_text = (
            f"🚨 [PantryPulse Alert] Emergency Food Rescue Dispatch!\n"
            f"Donor: {donation.donor_name} ({donation.donor_address.address})\n"
            f"Cargo: {donation.estimated_weight_lbs} lbs ({donation.item_description})\n"
            f"Pickup Code: {dispatch.pickup_verification_code}\n"
            f"Deliver to: {dispatch.pantry_address}\n"
            f"Open mission dashboard: https://pantrypulse.org/mission/{dispatch.id}"
        )
        msg_record = {
            "id": f"msg-{len(self._sent_messages) + 1}",
            "recipient_type": "VOLUNTEER",
            "recipient_name": volunteer.name,
            "recipient_phone": volunteer.phone,
            "channel": "SMS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": sms_text,
            "status": "DELIVERED"
        }
        self._sent_messages.append(msg_record)
        logger.info(f"[SMS -> {volunteer.name} ({volunteer.phone})]: {sms_text}")
        return True

    def notify_donor_eta(self, donation: DonationAlert, dispatch: Dispatch, volunteer: Volunteer, eta_minutes: int) -> bool:
        sms_text = (
            f"👋 [PantryPulse] Volunteer driver {volunteer.name} has been dispatched to collect your donation "
            f"at {donation.donor_name}. Estimated arrival in ~{eta_minutes} mins in a {volunteer.vehicle_type.value}. "
            f"Driver Pickup Code: {dispatch.pickup_verification_code}."
        )
        msg_record = {
            "id": f"msg-{len(self._sent_messages) + 1}",
            "recipient_type": "DONOR",
            "recipient_name": donation.donor_contact_name,
            "recipient_phone": donation.donor_phone,
            "channel": "SMS",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": sms_text,
            "status": "DELIVERED"
        }
        self._sent_messages.append(msg_record)
        logger.info(f"[SMS -> Donor {donation.donor_contact_name}]: {sms_text}")
        return True

    def notify_coordinator_urgent_decision(self, donation: DonationAlert) -> bool:
        alert_text = (
            f"⚠️ [PantryPulse Mission Control] New food rescue alert from {donation.donor_name} "
            f"({donation.estimated_weight_lbs} lbs {donation.food_category.value}). "
            f"Strands Agent generated a candidate proposal awaiting your approval."
        )
        msg_record = {
            "id": f"msg-{len(self._sent_messages) + 1}",
            "recipient_type": "COORDINATOR",
            "recipient_name": "Coordinator On Duty",
            "recipient_phone": "Dashboard Audio/Visual",
            "channel": "WEBHOOK_WEBSOCKET",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": alert_text,
            "status": "DELIVERED"
        }
        self._sent_messages.append(msg_record)
        logger.info(f"[Dashboard Alert]: {alert_text}")
        return True

    def get_sent_messages(self) -> List[Dict[str, Any]]:
        return list(reversed(self._sent_messages))
