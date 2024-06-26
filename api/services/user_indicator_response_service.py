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
        try:
            indicators = [(key, data[key]) for key in data if key.startswith(self.key)]

            for indicator_key, indicator_value in indicators:
                response_key = f"{indicator_key}_response"
                response_value = data.get(response_key)
                if response_value is not None:
                    user_response = self.class_model(
                        user_id=self.user_id,
                        user_phone=self.user_phone,
                        user_flow_id=self.user_flow_id,
                        indicator_question=indicator_value,
                        indicator_question_response=response_value,
                    )
                    db.session.add(user_response)

            db.session.commit()

            logger.info(f"Captured indicator responses for {self.user_phone}.")
        except Exception as e:
            logger.error(
                f"Error while capturing indicator responses. data: {data}."
                f"Error message: {e}"
            )
