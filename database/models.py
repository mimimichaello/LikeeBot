import datetime
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


class BaseUser(DeclarativeBase):
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now())

class BaseLinkUsage(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)



class MenuText(BaseSubscribe):
    __tablename__ = "menu_text"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)


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

    category: Mapped["Category"] = relationship("Category", backref="subscriptions")


class User(BaseSubscribe):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now())


    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    current_subscription_id: Mapped[int] = mapped_column(
        ForeignKey("subscribe.id"), nullable=True
    )
    subscription_end_date: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    link_sent: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    links_sent: Mapped[int] = mapped_column(Integer, default=0)

    current_subscription: Mapped["Subscribe"] = relationship("Subscribe", uselist=False)




class LinkUsage(BaseSubscribe):
    __tablename__ = "link_usage"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    links_sent: Mapped[int] = mapped_column(Integer, default=0)

    created: Mapped[DateTime] = mapped_column(DateTime, default=datetime.datetime.now)

    user: Mapped["User"] = relationship("User", backref="link_usage")
