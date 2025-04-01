from models import User, GlobalProduct, CalorieEntry, FavoriteProduct
from datetime import datetime, timedelta

# Текст для кнопок Reply-клавиатуры
text_search_global = "Найти базовое блюдо"
text_search_favorite = "Найти свое блюдо"
text_create_favorite = "Создать свое блюдо"
text_add_favorite_from_image = "Съесть свое блюдо по фото"
text_set_goal = "Изменить цель по калориям"
text_daily_stats = "Статистика за день"

# Функция получения характеристик собственного блюда
def favorite_product_stats(product : FavoriteProduct):
    stats = (
        f"Вес: {product.quantity:.0f}г\n"
        f"Калории: {product.calories:.0f}\n"
        f"Белки: {product.proteins:.0f}\n"
        f"Жиры: {product.fats:.0f}\n"
        f"Углеводы: {product.carbs:.0f}"
    )
    return stats

# Функция получения характеристик базового блюда
def global_product_stats(product : GlobalProduct):
    stats = (
        f"Калории: {product.calories:.0f}\n"
        f"Белки: {product.proteins:.0f}\n"
        f"Жиры: {product.fats:.0f}\n"
        f"Углеводы: {product.carbs:.0f}"
    )
    return stats

# Функция для получения статистики питания за указанную дату
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

    calories_str = f"Калории:  {total_calories:.0f}"
    if user.calorie_goal is not None:
        calories_str += f" / {user.calorie_goal} ккал"
    else:
        calories_str += " ккал"

    proteins_str = f"Белки:       {total_proteins:.0f}"
    if user.proteins_goal is not None:
        proteins_str += f" / {user.proteins_goal} г"
    else:
        proteins_str += " г"

    fats_str = f"Жиры:       {total_fats:.0f}"
    if user.fats_goal is not None:
        fats_str += f" / {user.fats_goal} г"
    else:
        fats_str += " г"

    carbs_str = f"Углеводы: {total_carbs:.0f}"
    if user.carbs_goal is not None:
        carbs_str += f" / {user.carbs_goal} г"
    else:
        carbs_str += " г"

    stats = (
        f"{calories_str}\n"
        f"{proteins_str}\n"
        f"{fats_str}\n"
        f"{carbs_str}\n"
    )
    return stats

# Функция создания записи о съедении базового блюда
def entry_from_global(product: GlobalProduct, user: User, quantity):
    entry = CalorieEntry(
        user_id=user.id,
        global_product_id=product.id,
        quantity=quantity,
        calories=product.calories,
        proteins=product.proteins,
        fats=product.fats,
        carbs=product.carbs,
    )
    return entry

# Функция создания записи о съедении собственного блюда
def entry_from_favorite(product: FavoriteProduct, user: User):
    entry = CalorieEntry(
        user_id=user.id,
        favorite_product_id=product.id,
        quantity=product.quantity,
        calories=product.calories,
        proteins=product.proteins,
        fats=product.fats,
        carbs=product.carbs,
    )
    return entry
