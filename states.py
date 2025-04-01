from aiogram.fsm.state import StatesGroup, State

# Состояния для команды /set_goal
class SetCalorieGoal(StatesGroup):
    waiting_for_calorie_goal = State()
    waiting_for_proteins_goal = State()
    waiting_for_fats_goal = State()
    waiting_for_carbs_goal = State()

# Состояния для команды /search_global
class SearchGlobalProduct(StatesGroup):
    waiting_for_search = State()
    waiting_for_add_quantity = State()
    waiting_for_favorite_quantity = State()
    waiting_for_favorite_name = State()

# Состояния для команды /search_favorite
class SearchFavoriteProduct(StatesGroup):
    waiting_for_search = State()

# Состояния для команды /create_favorite
class CreateFavoriteProduct(StatesGroup):
    waiting_for_name = State()
    waiting_for_quantity = State()
    waiting_for_calories = State()
    waiting_for_proteins = State()
    waiting_for_fats = State()
    waiting_for_carbs = State()
    waiting_for_image = State()

# Состояния для команды /favorite_from_image
class AddFavoriteFromImage(StatesGroup):
    waiting_for_image = State()

# Состояния для команды /daily_stats
class DailyStats(StatesGroup):
    waiting_for_date = State()
