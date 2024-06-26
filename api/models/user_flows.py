from datetime import date
from flask_sqlalchemy.query import Query as BaseQuery
from sqlalchemy import desc, func

from api import db
from api.mixins import TimestampMixin


class UserFlowsQuery(BaseQuery):
    def get_todays_latest_user_flow(self, flow_uuid, user_phone):
        return (
            self.filter(
                UserFlows.flow_uuid == flow_uuid,
                UserFlows.user_phone == user_phone,
                func.DATE(UserFlows.flow_start_time) == date.today(),
            )
            .order_by(desc("flow_start_time"))
            .first()
        )


class UserFlows(TimestampMixin, db.Model):
    query_class = UserFlowsQuery

    class FlowRunStatus:
        SENT = "sent"
        COMPLETED = "completed"
        ENDED = "ended"

    __tablename__ = "user_flows"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user_phone = db.Column(db.BigInteger, nullable=False, index=True)
    flow_uuid = db.Column(db.String(255), index=True)
    flow_name = db.Column(db.String(255))
    flow_type = db.Column(db.String(255))
    flow_run_status = db.Column(db.String(255))
    flow_start_time = db.Column(db.DateTime(timezone=True))
    flow_end_time = db.Column(db.DateTime(timezone=True))
    is_active = db.Column(db.Boolean)
