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

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id})>"


# class GlobalProduct(Base):
#     __tablename__ = 'global_products'
#
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False, unique=True)
#     calories = Column(Integer, nullable=False)
#     proteins = Column(Integer, nullable=False)
#     fats = Column(Integer, nullable=False)
#     carbs = Column(Integer, nullable=False)
#
#     def __repr__(self):
#         return f"<Product(name={self.name})>"
#
# class FavoriteProduct(Base):
#     __tablename__ = 'user_favorites'
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     product_id = Column(Integer, ForeignKey('global_products.id'), nullable=True)  # Опционально
#     custom_name = Column(String, nullable=True)  # Для пользовательских продуктов
#     calories = Column(Integer, nullable=False)
#     proteins = Column(Integer, nullable=False)
#     fats = Column(Integer, nullable=False)
#     carbs = Column(Integer, nullable=False)
#
#     user = relationship("User", back_populates="favorites")
#     global_product = relationship("GlobalProduct", back_populates="user_favorites")
#
# class CalorieEntry(Base):
#     __tablename__ = 'calorie_entries'
#
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     product_id = Column(Integer, ForeignKey('global_products.id'), nullable=True)
#     custom_product_id = Column(Integer, ForeignKey('user_favorites.id'), nullable=True)
#     quantity = Column(Integer, nullable=False)
#     date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
#
#     user = relationship("User", back_populates="entries")
#     global_product = relationship("GlobalProduct", back_populates="entries")
#     custom_product = relationship("UserFavorite", back_populates="entries")