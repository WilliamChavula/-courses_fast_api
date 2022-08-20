from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from models.session import Base
from utils import generate_id


class SubjectModel(Base):
    __tablename__ = "subject"

    id = Column(String, primary_key=True, default=generate_id)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)

    course = relationship(
        "CourseModel", back_populates="subject", cascade="all, delete",)

    def __repr__(self) -> str:
        return f"<SubjectModel id={self.id}, title={self.title}, slug={self.slug}>"
