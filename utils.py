from models import User, GlobalProduct, CalorieEntry, FavoriteProduct
from database import get_db

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


from datetime import datetime, timedelta

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
        if entry.global_product:
            total_calories += entry.global_product.calories * entry.quantity / 100
            total_proteins += entry.global_product.proteins * entry.quantity / 100
            total_fats += entry.global_product.fats * entry.quantity / 100
            total_carbs += entry.global_product.carbs * entry.quantity / 100
        else:
            total_calories += entry.favorite_product.calories * entry.quantity / 100
            total_proteins += entry.favorite_product.proteins * entry.quantity / 100
            total_fats += entry.favorite_product.fats * entry.quantity / 100
            total_carbs += entry.favorite_product.carbs * entry.quantity / 100

    stats = (
        f"Калории: {total_calories:.0f} ккал\n"
        f"Белки: {total_proteins:.0f} г\n"
        f"Жиры: {total_fats:.0f} г\n"
        f"Углеводы: {total_carbs:.0f} г"
    )
    return stats
