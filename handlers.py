from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from states import Form
from utils import get_temperature, get_food_info
#import aiohttp

router = Router()
user = {}

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.reply("Добро пожаловать! Я ваш бот для расчёта нормы воды, калорий и трекинга активности.\n"
                        "Для начала работы создайте анкету. Введите /set_profile для начала.")

#Создание формы. Просим пользователя ответить на все вопросы.
@router.message(Command("set_profile"))
async def start_form(message: Message, state: FSMContext):
    await message.reply("Введите ваш вес (в кг):")
    await state.set_state(Form.weight)

@router.message(Form.weight)
async def process_weight(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await message.reply("Введите ваш рост (в см):")
    await state.set_state(Form.height)

@router.message(Form.height)
async def process_height(message: Message, state: FSMContext):
    await state.update_data(height=message.text)
    await message.reply("Введите ваш возраст:")
    await state.set_state(Form.age)

@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Сколько минут активности у вас в день?")
    await state.set_state(Form.activity)

@router.message(Form.activity)
async def process_activity(message: Message, state: FSMContext):
    await state.update_data(activity=message.text)
    await message.reply("В каком городе вы находитесь?")
    await state.set_state(Form.city)

@router.message(Form.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.reply("Какая у вас цель по каллориям в день")
    await state.set_state(Form.callories)

@router.message(Form.callories)
async def process_callories(message: Message, state: FSMContext):
    global user
    await state.update_data(callories=message.text)
    #await message.reply(f"Проверьте данные {d.get('weight')} {d.get('height')} \n")
    data = await state.get_data()
    user = data
    print(f"DEBUG: Сохраненные данные: {user}")
    await message.reply("Спасибо за заполнение анкеты! \n"
                        "Чтобы увидеть норму воды и каллорий введите /calculate")
    await state.clear()

#Функция по дальнейшим шагам: рассчитать норму
@router.message(Command("calculate"))
async def calculate(message: Message):
    global user
    print(f"DEBUG: Данные для расчета: {user}")
    city = user['city']
    weight = float(user['weight'])
    height = float(user['height'])
    active = int(user['activity'])
    callories_aim = float(user['callories'])
    age = int(user['age'])
    # get_temperature
    temp = float(get_temperature(city))
    print(f"DEBUG: Данные по подключению к Weather API - результат температура: {temp}")
    # calculate water norm
    water = float(weight) * 30 + 500 * int(active) / 30 + 500 * temp / 25
    user['water_norm'] = water
    # check callories norm
    if callories_aim is None:
        callories_aim = 10 * weight + 6.25 * height - 5 * age + 200 * active / 30
        user['cal_norm'] = callories_aim
    else:
        user['cal_norm'] = callories_aim
    await message.answer(f"Норма воды: {water} \n"
                        f"Норма (или цель) каллорий: {callories_aim}\n"
                        f"Для внесения информации по потреблению воды, каллорий и пройденным активностям, введите /help")  #: {rate:.5f}")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Доступные команды:\n"
        "/log_water <количество> - Внести потребленную воду и посмотреть остаток до нормы\n"
        "/log_food <название продукта> - Сохраняет калорийность.\n"
        "/log_workout <тип тренировки> <время (мин)> - Фиксирует сожжённые калории.\n"
        "/check_progress - Прогресс по воде и калориям")

#логгируем воду
@router.message(Command("log_water"))
async def cmd_water(
        message: Message,
        command: CommandObject
):
    global user
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    else:
        water_log = int(command.args)
    water_norm = int(user['water_norm'])
    if 'water_log' not in user.keys():
        user['water_log'] = water_log
    else:
        user['water_log'] += water_log

    water_diff = water_norm - user['water_log']
    if water_diff >0:
        await message.answer(f"До выполнения нормы осталось {water_diff} мл")
    else:
        await message.answer(f"Норма выполнена!")

#логгируем каллории
@router.message(Command("log_food"))
async def cmd_food(
        message: Message,
        command: CommandObject
):
    global user
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    else:
        food = command.args
    callory = get_food_info(food)
    print(f"DEBUG: Данные по подключению к Food API - result: {callory}")
    user['callory'] = float(callory['calories'])
    await message.answer(f"{food} - {user['callory']} каллорий. Сколько грамм вы съели?")

@router.message()
async def log_apifood(message: Message):
    global user
    gram = float(message.text)
    prod_callory = gram/100 * user['callory']
    if 'cal_log' not in user.keys():
        user['cal_log'] = prod_callory
    else:
        user['cal_log'] += prod_callory
    await message.answer(f"Записано {prod_callory} ккал")

#запись тренировки
@router.message(Command("log_workout"))
async def cmd_workout(
        message: Message,
        command: CommandObject
):
    global user
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        work_type, work_time = command.args.split(" ", maxsplit=1)
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/log_workout <тип> <время в мин>"
        )

    weight = float(user['weight'])
    off_call = 6 * float(work_time)/60.0 *  weight
    water_needed = 200 * float(work_time)/30.0
    user['needed_water'] = water_needed
    user['off_calories'] = off_call
    await message.answer(f"{work_type} {work_time} минут - {off_call} ккал. \n"
                         f"Дополнительно выпейте {water_needed} мл воды.")

# Функция для подключения обработчиков
def setup_handlers(dp):
    dp.include_router(router)