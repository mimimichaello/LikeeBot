from sqlalchemy import Column, Integer, String, Text, Float, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseSubscribe(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


class Subscribe(BaseSubscribe):
    __tablename__ = "subscribe"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    price: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
