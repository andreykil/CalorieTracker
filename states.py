from aiogram.fsm.state import StatesGroup, State

class SetCalorieGoal(StatesGroup):
    waiting_for_calorie_goal = State()

class SearchGlobalProduct(StatesGroup):
    waiting_for_search = State()
    waiting_for_add_quantity = State()
    waiting_for_favorite_quantity = State()
    waiting_for_favorite_name = State()

class SearchFavoriteProduct(StatesGroup):
    waiting_for_search = State()

class CreateFavoriteProduct(StatesGroup):
    waiting_for_name = State()
    waiting_for_quantity = State()
    waiting_for_calories = State()
    waiting_for_proteins = State()
    waiting_for_fats = State()
    waiting_for_carbs = State()
