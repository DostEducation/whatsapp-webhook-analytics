import re
from typing import Any

from api import db, models
from api.utils.loggingutils import logger


class UserAttributeService:
    def __init__(self, user):
        self.user_id = user.id
        self.user_phone = user.phone
        self.class_model = models.UserAttributes

    def handle_contact_fields_data(self, contact_data: dict[str, Any]):
        try:
            contact_fields_data = contact_data.get("fields", {})
            existing_attributes = self.class_model.query.get_existing_user_attributes(
                self.user_id
            )
            for field_key, field_value in contact_fields_data.items():
                if not re.match(r"^\w+$", field_key):
                    logger.error(
                        f"Found a contact variable {field_key} for {self.user_phone} "
                        "with special character which can't be processed."
                    )
                    continue
                elif field_key.lower() == "name":
                    continue

                value = field_value.get("value")
                user_attribute = existing_attributes.get(field_key)

                if user_attribute:
                    if user_attribute.field_value != value:
                        user_attribute.field_value = value
                else:
                    user_attribute = self.create_user_attribute(field_key, value)
                    db.session.add(user_attribute)

            db.session.commit()
        except Exception as e:
            logger.error(
                f"Error occured while handling contact fields data. Error: {e}"
            )

    def create_user_attribute(
        self, field_key: str, value: str
    ) -> models.UserAttributes:
        user_attribute = self.class_model(
            user_id=self.user_id,
            user_phone=self.user_phone,
            field_name=field_key,
            field_value=value,
        )
        return user_attribute
