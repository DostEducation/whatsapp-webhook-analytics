import enum
from api import db
from api.mixins import TimestampMixin


class ActorType(enum.Enum):
    USER = "user"
    GPT = "gpt"
    BHASHINI = "bhashini"


class MessageTransaction(TimestampMixin, db.Model):
    __tablename__ = "message_transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    user_phone = db.Column(db.BigInteger, index=True)
    user_flow_id = db.Column(db.Integer, db.ForeignKey("user_flows.id"), index=True)
    flow_uuid = db.Column(db.String(100), index=True)
    flow_name = db.Column(db.String(255))
    flow_type = db.Column(db.String(50))
    flow_status = db.Column(db.String(50))
    organization_id = db.Column(db.Integer, index=True)
    source = db.Column(db.Enum(ActorType), nullable=False, index=True)
    destination = db.Column(db.Enum(ActorType), nullable=False, index=True)
    message_text = db.Column(db.Text, nullable=True)
    raw_payload = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=False, index=True)
    sequence_in_flow = db.Column(db.Integer, nullable=True)
    entry_activity_key = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return (
            f"<MessageTransaction {self.source.value} -> {self.destination.value} "
            f"user_id={self.user_id} flow_uuid={self.flow_uuid}>"
        )
