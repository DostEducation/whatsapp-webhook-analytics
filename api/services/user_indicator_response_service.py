from typing import Any

from api import db, models
from api.utils.loggingutils import logger


class UserIndicatorResponseService:
    def __init__(self, user: models.Users, user_flow: models.UserFlows):
        self.key: str = "indicator_question"  # Prefix for the indicators key in payload
        self.user_id: int = user.id
        self.user_phone: int = user.phone
        self.user_flow_id: int = user_flow.id
        self.class_model = models.UserIndicatorResponses

    def process_user_indicator_responses(self, data: dict[str, Any]) -> None:
        logger.debug(
            f"Started to process indicator responses for {self.user_phone} data: {data}"
        )
        try:
            indicators = [(key, data[key]) for key in data if key.startswith(self.key)]
            logger.debug(f"Filtered indicator keys: {[k for k, _ in indicators]}")

            if not indicators:
                logger.warning(
                    f"No indicator keys found for {self.user_phone}. Data: {data}"
                )

            for indicator_key, indicator_value in indicators:
                logger.debug(
                    f"Processing key: {indicator_key} with value: {indicator_value}"
                )
                response_key = f"{indicator_key}_response"
                response_value = data.get(response_key)

                if response_value is not None:
                    logger.debug(
                        f"Found response for key {response_key}: {response_value}"
                    )
                    user_response = self.class_model(
                        user_id=self.user_id,
                        user_phone=self.user_phone,
                        user_flow_id=self.user_flow_id,
                        indicator_question=indicator_value,
                        indicator_question_response=response_value,
                    )
                    db.session.add(user_response)
                    logger.debug(f"Added response object to session: {user_response}")
                else:
                    logger.warning(f"No response found for key {indicator_key}")

            db.session.commit()
            logger.info(f"Captured indicator responses for {self.user_phone}.")

        except Exception as e:
            logger.error(
                f"Failed to process indicator responses for {self.user_phone}: {e}",
                exc_info=True,
            )
