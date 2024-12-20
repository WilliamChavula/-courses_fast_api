from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from models.session import Base
from utils import generate_id


class ModuleModel(Base):
    __tablename__ = "module"

    id = Column(String, primary_key=True, default=generate_id)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=False)

    course = relationship(
        "CourseModel",
        back_populates="module",
        cascade="all, delete",
    )

    def __repr__(self):
        return f"ModuleModel(id={self.id}, title={self.title}, description={self.description}, course={self.course})"
