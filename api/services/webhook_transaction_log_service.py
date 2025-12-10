import json
from typing import Any, Optional

from api import models
from api.utils import db_utils
from api.utils.loggingutils import logger


class WebhookTransactionLogService:
    def create_new_webhook_log(
        self, json_data: dict[str, Any]
    ) -> Optional[models.WebhookTransactionLog]:
        try:
            data: str = json.dumps(json_data)
            new_webhook_log: models.WebhookTransactionLog = (
                models.WebhookTransactionLog(
                    payload=data,
                    processed=False,
                    attempts=0,
                )
            )
            db_utils.save(new_webhook_log)
            return new_webhook_log
        except Exception as e:
            logger.error(
                f"Error while creating new webhook log. Webhook: {json_data}."
                f"Error message: {e}"
            )
            return None

    def mark_webhook_log_as_processed(
        self, webhook_log: models.WebhookTransactionLog
    ) -> Optional[models.WebhookTransactionLog]:
        try:
            webhook_log.processed = True
            db_utils.save(webhook_log)
            return webhook_log
        except Exception as e:
            logger.error(
                f"Error marking webhook log as processed." f"Error message: {e}"
            )
            return None
