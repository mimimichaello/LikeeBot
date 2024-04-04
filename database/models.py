from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    func,
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseSubscribe(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class BeseUser(DeclarativeBase):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now())


class MenuText(BaseSubscribe):
    __tablename__ = "menu_text"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)


class Category(BaseSubscribe):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)


class Subscribe(BaseSubscribe):
    __tablename__ = "subscribe"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("category.id", ondelete="CASCADE"), nullable=False
    )

    category: Mapped["Category"] = relationship(backref="subscribe")


class User(BeseUser):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    current_subscription_id: Mapped[int] = mapped_column(
        ForeignKey("subscribe.id"), nullable=True
    )
    subscription_end_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    current_subscription: Mapped["Subscribe"] = relationship("Subscribe")
