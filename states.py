from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()
    callories = State()
    water_norm = State()
    callories_norm = State()
    water_log = State()
    callories_log = State()
    workout_log = State()
