import json

from api import models
from api.helpers import db_helper
from api.utils.loggingutils import logger


class WebhookTransactionLogService:
    def create_new_webhook_log(self, jsonData):
        try:
            data = json.dumps(jsonData)
            new_webhook_log = models.WebhookTransactionLog(
                payload=data,
                processed=False,
                attempts=0,
            )
            db_helper.save(new_webhook_log)
            return new_webhook_log
        except Exception as e:
            logger.error(
                f"Error while creating new webhook log. Webhook: {jsonData}."
                f"Error message: {e}"
            )
            return None

    def mark_webhook_log_as_processed(self, webhook_log):
        try:
            webhook_log.processed = True
            db_helper.save(webhook_log)
        except Exception as e:
            logger.error(
                f"Error while marking webhook log as processed."
                f"Error message: {e}"
            )
            return None
