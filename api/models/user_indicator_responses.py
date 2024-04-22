from api import db
from api.mixins import TimestampMixin


class UserIndicatorResponses(TimestampMixin, db.Model):

    __tablename__ = "user_indicator_responses"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user_flow_id = db.Column(db.Integer, db.ForeignKey("user_flows.id"))
    indicator_question = db.Column(db.String(255))
    indicator_question_response = db.Column(db.String(255))
