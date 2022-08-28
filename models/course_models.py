from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from models.session import Base
from utils import generate_id


class CourseModel(Base):
    __tablename__ = "course"

    id = Column(String, primary_key=True, default=generate_id)
    module_id = Column(String, ForeignKey("module.id", ondelete="CASCADE"))
    subject_id = Column(String, ForeignKey("subject.id", ondelete="CASCADE"))
    owner = Column(String, nullable=False)
    title = Column(String(200), nullable=False)
    slug = Column(String, nullable=False)
    overview = Column(String, nullable=False)
    created = Column(DateTime, nullable=False)

    module = relationship("ModuleModel", back_populates="course")
    subject = relationship("SubjectModel", back_populates="course")

    def __repr__(self) -> str:
        return (
            f"<CourseModel id={self.id}, owner={self.owner}, title={self.title}, slug={self.slug}, "
            f"overview={self.overview}, module_id={self.module_id}, subject_id={self.subject_id}, "
            f"created={self.created}>"
        )
