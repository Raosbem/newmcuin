import uuid
import enum
from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    STAFF    = "staff"
    ADMIN    = "admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email           = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name       = Column(String(255), nullable=False)
    role            = Column(Enum(UserRole, values_callable=lambda obj: [e.value for e in obj], name="userrole", create_type=False), default=UserRole.CUSTOMER, nullable=False)
    is_active       = Column(Boolean, default=True, nullable=False)