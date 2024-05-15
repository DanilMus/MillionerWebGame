import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)
    record: so.Mapped[int] = so.mapped_column(sa.Integer, sa.CheckConstraint('record>=0'))

    # Как печатать объекты этого класса
    def __repr__(self):
        return '<User {}>'.format(self.username)

class Question(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    level: so.Mapped[int] = so.mapped_column()
    question: so.Mapped[str] = so.mapped_column(sa.String(255))
    answer_1: so.Mapped[str] = so.mapped_column(sa.String(63))
    answer_2: so.Mapped[str] = so.mapped_column(sa.String(63))
    answer_3: so.Mapped[str] = so.mapped_column(sa.String(63))
    answer_4: so.Mapped[str] = so.mapped_column(sa.String(63))
    num_answer: so.Mapped[int] = so.mapped_column()
    
    # Как печатать объекты этого класса
    def __repr__(self):
        return '<Question {}>'.format(self.question)