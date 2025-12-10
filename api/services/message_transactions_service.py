import json
from datetime import datetime
from typing import Any, Optional

from api import db, models
from api.helpers import common_helper
from api.utils.loggingutils import logger


class MessageTransactionService:
    """
    Handles all message-level transactions between:
      - User <-> GPT
      - User <-> Bhashini
      - GPT <-> Bhashini
    and links them to Users + UserFlows.
    """

    def __init__(self, user: models.Users, user_flow: models.UserFlows):
        self.user = user
        self.user_flow = user_flow
        self.class_model = models.MessageTransaction

    def capture_from_webhook(self, json_data: dict[str, Any]) -> None:
        """Parse the webhook payload and create message transaction records.

        Currently handles:
          - user_ask                    -> User -> GPT
          - ai_response                 -> GPT -> User
          - user_ask                    -> User -> Bhashini
          - bahshini_stt_translation    -> Bhashini -> GPT
          - ai_response                 -> GPT -> Bhashini
          - bahshini_tts_translation    -> Bhashini -> User
        """
        try:
            current_time = common_helper.get_current_utc_timestamp()

            user_ask: Optional[str] = json_data.get("user_ask")
            ai_response: Optional[str] = json_data.get("ai_response")
            bhashini_stt: Optional[str] = json_data.get("bahshini_stt_translation")
            bhashini_tts: Optional[str] = json_data.get("bahshini_tts_translation")

            flow_uuid = json_data.get("flow_uuid")
            flow_name = json_data.get("flow_name")
            flow_type = json_data.get("flow_type")
            flow_status = json_data.get("flow_status")
            organization_id = json_data.get("organization_id")

            entry_activity_key = self._extract_entry_activity_key(json_data)

            # ---------- User <-> GPT ----------
            if user_ask:
                # User -> GPT
                self._create_message_transaction(
                    source=models.ActorType.USER,
                    destination=models.ActorType.GPT,
                    message_text=user_ask,
                    current_time=current_time,
                    flow_uuid=flow_uuid,
                    flow_name=flow_name,
                    flow_type=flow_type,
                    flow_status=flow_status,
                    organization_id=organization_id,
                    entry_activity_key=entry_activity_key,
                    raw_payload=json_data,
                )

            if ai_response:
                # GPT -> User
                self._create_message_transaction(
                    source=models.ActorType.GPT,
                    destination=models.ActorType.USER,
                    message_text=ai_response,
                    current_time=current_time,
                    flow_uuid=flow_uuid,
                    flow_name=flow_name,
                    flow_type=flow_type,
                    flow_status=flow_status,
                    organization_id=organization_id,
                    entry_activity_key=entry_activity_key,
                    raw_payload=json_data,
                )

            # ---------- User <-> Bhashini ----------
            if user_ask:
                # User -> Bhashini (same original user text, before STT/translation)
                self._create_message_transaction(
                    source=models.ActorType.USER,
                    destination=models.ActorType.BHASHINI,
                    message_text=user_ask,
                    current_time=current_time,
                    flow_uuid=flow_uuid,
                    flow_name=flow_name,
                    flow_type=flow_type,
                    flow_status=flow_status,
                    organization_id=organization_id,
                    entry_activity_key=entry_activity_key,
                    raw_payload=json_data,
                )

            if bhashini_stt:
                # Bhashini -> GPT (STT/translation output that GPT actually sees)
                self._create_message_transaction(
                    source=models.ActorType.BHASHINI,
                    destination=models.ActorType.GPT,
                    message_text=bhashini_stt,
                    current_time=current_time,
                    flow_uuid=flow_uuid,
                    flow_name=flow_name,
                    flow_type=flow_type,
                    flow_status=flow_status,
                    organization_id=organization_id,
                    entry_activity_key=entry_activity_key,
                    raw_payload=json_data,
                )

            # ---------- GPT <-> Bhashini ----------
            if ai_response:
                # GPT -> Bhashini (text that will be turned into TTS)
                self._create_message_transaction(
                    source=models.ActorType.GPT,
                    destination=models.ActorType.BHASHINI,
                    message_text=ai_response,
                    current_time=current_time,
                    flow_uuid=flow_uuid,
                    flow_name=flow_name,
                    flow_type=flow_type,
                    flow_status=flow_status,
                    organization_id=organization_id,
                    entry_activity_key=entry_activity_key,
                    raw_payload=json_data,
                )

            if bhashini_tts:
                # Bhashini -> User (final synthesized response)
                self._create_message_transaction(
                    source=models.ActorType.BHASHINI,
                    destination=models.ActorType.USER,
                    message_text=bhashini_tts,
                    current_time=current_time,
                    flow_uuid=flow_uuid,
                    flow_name=flow_name,
                    flow_type=flow_type,
                    flow_status=flow_status,
                    organization_id=organization_id,
                    entry_activity_key=entry_activity_key,
                    raw_payload=json_data,
                )

            db.session.commit()
            logger.info(
                "Captured message transactions for user %s, flow_uuid=%s",
                self.user.phone,
                flow_uuid,
            )

        except Exception as e:
            logger.error(
                "Error while capturing message transactions for user %s. Error: %s",
                self.user.phone,
                e,
                exc_info=True,
            )
            db.session.rollback()

    def _create_message_transaction(
        self,
        source: models.ActorType,
        destination: models.ActorType,
        message_text: str,
        current_time: datetime,
        flow_uuid: Optional[str],
        flow_name: Optional[str],
        flow_type: Optional[str],
        flow_status: Optional[str],
        organization_id: Optional[int],
        entry_activity_key: Optional[str],
        raw_payload: dict[str, Any],
    ) -> models.MessageTransaction:
        tx = self.class_model(
            user_id=self.user.id,
            user_phone=self.user.phone,
            user_flow_id=self.user_flow.id,
            flow_uuid=flow_uuid,
            flow_name=flow_name,
            flow_type=flow_type or "activity",
            flow_status=flow_status,
            organization_id=organization_id,
            source=source,
            destination=destination,
            message_text=message_text,
            raw_payload=json.dumps(raw_payload),
            sent_at=current_time,
            entry_activity_key=entry_activity_key,
        )
        db.session.add(tx)
        return tx

    def _extract_entry_activity_key(self, json_data: dict[str, Any]) -> Optional[str]:
        """Optional helper to map 'which activity triggered AI'.

        For example: look for any 'activity_*_started' key and use the latest one.
        You can refine this logic based on your real payloads.
        """
        activity_keys = [
            key
            for key in json_data.keys()
            if key.startswith("activity_") and key.endswith("_started")
        ]
        if not activity_keys:
            return None

        return sorted(activity_keys)[-1]
