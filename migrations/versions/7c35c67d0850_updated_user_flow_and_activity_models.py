"""Updated user flow and activity models.

Revision ID: 7c35c67d0850
Revises: cf56b46971fa
Create Date: 2024-05-07 20:59:49.391599
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7c35c67d0850"
down_revision = "cf56b46971fa"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user_activities", schema=None) as batch_op:
        batch_op.alter_column("is_started", existing_type=sa.BOOLEAN(), nullable=True)
        batch_op.alter_column("is_succeeded", existing_type=sa.BOOLEAN(), nullable=True)
        batch_op.alter_column("is_completed", existing_type=sa.BOOLEAN(), nullable=True)

    with op.batch_alter_table("user_flows", schema=None) as batch_op:
        batch_op.alter_column("is_active", existing_type=sa.BOOLEAN(), nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("user_flows", schema=None) as batch_op:
        batch_op.alter_column("is_active", existing_type=sa.BOOLEAN(), nullable=False)

    with op.batch_alter_table("user_activities", schema=None) as batch_op:
        batch_op.alter_column(
            "is_completed", existing_type=sa.BOOLEAN(), nullable=False
        )
        batch_op.alter_column(
            "is_succeeded", existing_type=sa.BOOLEAN(), nullable=False
        )
        batch_op.alter_column("is_started", existing_type=sa.BOOLEAN(), nullable=False)

    # ### end Alembic commands ###
