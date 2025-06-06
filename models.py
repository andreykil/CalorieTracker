from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

from sqlalchemy.orm import relationship

Base = declarative_base()

# Модель пользователя бота
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    calorie_goal = Column(Integer, nullable=True)
    proteins_goal = Column(Integer, nullable=True)
    fats_goal = Column(Integer, nullable=True)
    carbs_goal = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    favorites = relationship("FavoriteProduct", back_populates="user")
    entries = relationship("CalorieEntry", back_populates="user")

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id})>"

# Модель продукта из общего списка
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

# Модель собственного продукта пользователя
class FavoriteProduct(Base):
    __tablename__ = 'favorite_products'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    global_product_id = Column(Integer, ForeignKey('global_products.id'), nullable=True)
    name = Column(String, nullable=False)
    calories = Column(Integer, nullable=False)
    proteins = Column(Integer, nullable=False)
    fats = Column(Integer, nullable=False)
    carbs = Column(Integer, nullable=False)
    feature_vector = Column(String, nullable=True)

    user = relationship("User", back_populates="favorites")
    global_product = relationship("GlobalProduct", back_populates="favorite_products")
    entries = relationship("CalorieEntry", back_populates="favorite_product")

    def __repr__(self):
        return f"<FavoriteProduct(user_id={self.user_id}, name={self.name or self.global_product.name})>"

# Модель записи о съеденном продукте
class CalorieEntry(Base):
    __tablename__ = 'calorie_entries'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    global_product_id = Column(Integer, ForeignKey('global_products.id'), nullable=True)
    favorite_product_id = Column(Integer, ForeignKey('favorite_products.id'), nullable=True)
    quantity = Column(Integer, nullable=False)
    calories = Column(Integer, nullable=False)
    proteins = Column(Integer, nullable=False)
    fats = Column(Integer, nullable=False)
    carbs = Column(Integer, nullable=False)
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="entries")
    global_product = relationship("GlobalProduct", back_populates="entries")
    favorite_product = relationship("FavoriteProduct", back_populates="entries")
