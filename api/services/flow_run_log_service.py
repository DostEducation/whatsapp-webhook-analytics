from api import models
from api.helpers import common_helper
from api.utils import db_utils
from api.utils.loggingutils import logger


class FlowRunLogService:
    def __init__(self, user):
        self.user = user
        self.class_model = models.UserFlows

    def create_user_flow_log(self, json_data):
        try:
            flow_uuid = json_data.get("flow_uuid")
            flow_name = json_data.get("flow_name")
            flow_type = json_data.get("flow_type")
            flow_status = json_data.get("flow_status")

            latest_flow_log = self.class_model.query.get_todays_latest_user_flow(
                flow_uuid, self.user.phone
            )

            user_flow_log = None

            if flow_status == self.class_model.FlowRunStatus.STARTED:
                user_flow_log = self.create_log(flow_uuid, flow_name, flow_type)
            elif flow_status == self.class_model.FlowRunStatus.COMPLETED:
                user_flow_log = self.update_log(latest_flow_log)
            else:
                logger.error(
                    f"Got unexpected flow status {flow_status}. Flow name {flow_name}."
                )

            return user_flow_log
        except Exception as e:
            logger.error(
                f"Error while creating new user flow log. json data: {json_data}."
                f"Error message: {e}"
            )
            raise

    def create_log(self, flow_uuid, flow_name, flow_type):
        user_flow_log = self.class_model(
            user_id=self.user.id,
            user_phone=self.user.phone,
            flow_uuid=flow_uuid,
            flow_name=flow_name,
            flow_type=flow_type,
            flow_run_status=self.class_model.FlowRunStatus.STARTED,
            flow_start_time=common_helper.get_ist_timestamp(),
            is_active=True,
        )

        db_utils.save(user_flow_log)
        logger.info(f"Created a user flow log for phone number {self.user.phone}.")
        return user_flow_log

    def update_log(self, latest_flow_log):
        latest_flow_log.flow_run_status = self.class_model.FlowRunStatus.COMPLETED
        latest_flow_log.flow_end_time = common_helper.get_ist_timestamp()
        latest_flow_log.is_active = False

        db_utils.save(latest_flow_log)
        logger.info(f"Updated user flow log for phone number {self.user.phone}.")
        return latest_flow_log