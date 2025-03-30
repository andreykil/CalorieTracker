from models import User, GlobalProduct, CalorieEntry, FavoriteProduct
from database import get_db
from io import BytesIO
from datetime import datetime, timedelta

from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.models import Model
from tensorflow.keras.layers import GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input
import numpy as np
import json


base_model = ResNet50(weights='imagenet', include_top=False)
x = base_model.output
x = GlobalAveragePooling2D()(x)
feature_model = Model(inputs=base_model.input, outputs=x)

def extract_feature_vector(file_data: bytes) -> np.ndarray:
    img = load_img(BytesIO(file_data), target_size=(224, 224))
    img_array = img_to_array(img)
    img_array = preprocess_input(np.expand_dims(img_array, axis=0))
    feature_vector = feature_model.predict(img_array)[0]
    return feature_vector

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def favorite_product_stats(product : FavoriteProduct):
    stats = (
        f"Вес: {product.quantity:.0f}г\n"
        f"Калории: {product.calories:.0f}\n"
        f"Белки: {product.proteins:.0f}\n"
        f"Жиры: {product.fats:.0f}\n"
        f"Углеводы: {product.carbs:.0f}"
    )
    return stats

def global_product_stats(product : GlobalProduct):
    stats = (
        f"Калории: {product.calories:.0f}\n"
        f"Белки: {product.proteins:.0f}\n"
        f"Жиры: {product.fats:.0f}\n"
        f"Углеводы: {product.carbs:.0f}"
    )
    return stats


def get_daily_stats(user, target_date):
    start_of_day = datetime(target_date.year, target_date.month, target_date.day)
    end_of_day = start_of_day + timedelta(days=1)

    daily_entries = [entry for entry in user.entries if start_of_day <= entry.date < end_of_day]

    if not daily_entries:
        return "За этот день нет записей."

    total_calories = 0
    total_proteins = 0
    total_fats = 0
    total_carbs = 0
    for entry in daily_entries:
        total_calories += entry.calories * entry.quantity / 100
        total_proteins += entry.proteins * entry.quantity / 100
        total_fats += entry.fats * entry.quantity / 100
        total_carbs += entry.carbs * entry.quantity / 100

    stats = (
        f"Калории: {total_calories:.0f} ккал\n"
        f"Белки: {total_proteins:.0f} г\n"
        f"Жиры: {total_fats:.0f} г\n"
        f"Углеводы: {total_carbs:.0f} г"
    )
    return stats

def entry_from_product(product, user: User, quantity):
    if not quantity:
        quantity = product.quantity
    entry = CalorieEntry(
        user_id=user.id,
        favorite_product_id=product.id,
        quantity=quantity,
        calories=product.calories,
        proteins=product.proteins,
        fats=product.fats,
        carbs=product.carbs,
    )
    return entry
