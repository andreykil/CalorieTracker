from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, nullable=True)
    calorie_goal = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    favorites = relationship("FavoriteProduct", back_populates="user")
    entries = relationship("CalorieEntry", back_populates="user")

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id})>"


class GlobalProduct(Base):
    __tablename__ = 'global_products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    calories = Column(Integer, nullable=False)
    proteins = Column(Integer, nullable=False)
    fats = Column(Integer, nullable=False)
    carbs = Column(Integer, nullable=False)

    favorite_products = relationship("FavoriteProduct", back_populates="global_product")
    entries = relationship("CalorieEntry", back_populates="global_product")

    def __repr__(self):
        return f"<GlobalProduct(name={self.name})>"

class FavoriteProduct(Base):
    __tablename__ = 'favorite_products'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('global_products.id'), nullable=True)
    custom_name = Column(String, nullable=True)
    calories = Column(Integer, nullable=False)
    proteins = Column(Integer, nullable=False)
    fats = Column(Integer, nullable=False)
    carbs = Column(Integer, nullable=False)

    user = relationship("User", back_populates="favorites")
    global_product = relationship("GlobalProduct", back_populates="favorite_products")
    entries = relationship("CalorieEntry", back_populates="favorite_product")

    def __repr__(self):
        return f"<FavoriteProduct(user_id={self.user_id}, name={self.custom_name or self.global_product.name})>"

class CalorieEntry(Base):
    __tablename__ = 'calorie_entries'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('global_products.id'), nullable=True)
    favorite_product_id = Column(Integer, ForeignKey('favorite_products.id'), nullable=True)
    quantity = Column(Integer, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="entries")
    global_product = relationship("GlobalProduct", back_populates="entries")
    favorite_product = relationship("FavoriteProduct", back_populates="entries")