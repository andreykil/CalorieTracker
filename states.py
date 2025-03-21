from aiogram.fsm.state import StatesGroup, State

class SetCalorieGoal(StatesGroup):
    waiting_for_calorie_goal = State()

class AddGlobalProduct(StatesGroup):
    waiting_for_quantity = State()
    waiting_for_search = State()