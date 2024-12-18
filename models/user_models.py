import uuid
from sqlalchemy import Boolean, Column, DateTime, func, String

from models.session import Base


class UserModel(Base):
    __tablename__ = "user"

    id = Column(String, primary_key=True, nullable=False, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String, nullable=False)
    password = Column(String)
    job_title = Column(String(150), nullable=False)
    is_super_user = Column(Boolean, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<UserModel id={self.id}, first_name={self.first_name}, last_name={self.last_name}, "
            f" email={self.email}, job_title={self.job_title}, "
            f"is_super_user={self.is_super_user}, created_at={self.created_at}>"
        )
