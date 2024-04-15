from agraffe import Agraffe
from fastapi import FastAPI

from app.services import WebhookTransactionLogService
from app.utils.loggingutils import logger

app = FastAPI()


def handle_payload(request):
    if request.method == "POST":
        try:
            jsonData = request.get_json()
            if jsonData:
                handle_webhook(jsonData)
        except Exception as e:
            logger.error(
                f"Exception occured while handling the webhook payload: {jsonData}. Error: {e}"
            )
        return jsonData
    else:
        return "System does not accepts GET request"


def handle_webhook(jsonData):
    transaction_log_service = WebhookTransactionLogService()
    webhook_log = transaction_log_service.create_new_webhook_log(jsonData)
    transaction_log_service.mark_webhook_log_as_processed(webhook_log)


handler = Agraffe.entry_point(app)