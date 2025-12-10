import functions_framework

from api import app
from api.services import (
    FlowRunLogService,
    UserActivitiesService,
    UserAttributeService,
    UserCreationService,
    UserIndicatorResponseService,
    WebhookTransactionLogService,
    MessageTransactionService,
)
from api.utils.loggingutils import logger


# Endpoint for Cloud function
@functions_framework.http
def handle_payload(request):
    if request.method == "POST":
        with app.app_context():
            try:
                json_data = request.get_json()
                if not json_data:
                    return "The request cannot be processed", 400

                webhook_log = handle_webhook(json_data)
                return {
                    "success_message": f"You are onboarded.{webhook_log.id}",
                    "status_code": 200,
                }, 200
            except Exception as e:
                logger.error(
                    f"Exception while handling the webhook payload: {json_data}"
                    f"Error: {e}"
                )
            return "Success", 200
    else:
        return (
            "HTTP method used for the request is not valid at the requested URL",
            405,
        )


def handle_webhook(json_data):
    transaction_log_service = WebhookTransactionLogService()
    webhook_log = transaction_log_service.create_new_webhook_log(json_data)

    contact_data = json_data["contact"]
    if contact_data:
        user = handle_user_creation_from_contact(contact_data)
        user_flow = handle_user_flow_logs(user, json_data)
        handle_flow_activity_data(user, user_flow, json_data)
        process_user_indicators(user, user_flow, json_data)
        process_contact_data(user, contact_data)
        message_tx_service = MessageTransactionService(user, user_flow)
        message_tx_service.capture_from_webhook(json_data)

    webhook_log = transaction_log_service.mark_webhook_log_as_processed(webhook_log)
    return webhook_log


def handle_user_creation_from_contact(contact_data):
    user_creation_service = UserCreationService()
    return user_creation_service.create_new_user(contact_data)


def handle_user_flow_logs(user, json_data):
    flow_run_log_service = FlowRunLogService(user)
    return flow_run_log_service.create_user_flow_log(json_data)


def handle_flow_activity_data(user, user_flow, json_data):
    user_activities_service = UserActivitiesService(user, user_flow)
    user_activities_service.handle_user_activities(json_data)


def process_user_indicators(
    user,
    user_flow,
    json_data,
):
    user_indicator_res_service = UserIndicatorResponseService(user, user_flow)
    user_indicator_res_service.process_user_indicator_responses(json_data)
    return True


def process_contact_data(user, contact_data):
    user_attribute_service = UserAttributeService(user)
    user_attribute_service.handle_contact_fields_data(contact_data)
