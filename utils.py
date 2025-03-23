from models import User, GlobalProduct, CalorieEntry, FavoriteProduct

def info_favorite_product(product : FavoriteProduct) -> str:
    return  (
        f"Вес: {product.quantity:.0f}г\n"
        f"Калории: {product.calories:.0f}\n"
        f"Белки: {product.proteins:.0f}\n"
        f"Жиры: {product.fats:.0f}\n"
        f"Углеводы: {product.carbs:.0f}"
    )

def info_global_product(product : GlobalProduct) -> str:
    return  (
        f"В 100г:\n"
        f"Калории: {product.calories:.0f}\n"
        f"Белки: {product.proteins:.0f}\n"
        f"Жиры: {product.fats:.0f}\n"
        f"Углеводы: {product.carbs:.0f}"
    )