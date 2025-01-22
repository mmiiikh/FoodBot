from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from states import Form
from utils import get_temperature, get_food_info
#import aiohttp

router = Router()

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
    await state.update_data(callories=message.text)
    #await message.reply(f"Проверьте данные {d.get('weight')} {d.get('height')} \n")
    data = await state.get_data()
    print(f"DEBUG: Сохраненные данные: {data}")
    await message.reply("Спасибо за заполнение анкеты! \n"
                        "Чтобы увидеть норму воды и каллорий введите /calculate")

#Функция по дальнейшим шагам: рассчитать норму
@router.message(Command("calculate"))
async def calculate(message: Message, state: FSMContext):
    data = await state.get_data()

    print(f"DEBUG: Данные для расчета: {data}")
    #get_temperature
    #temp = get_temperature(str(data.get('city')))
    #calculate water norm
    if data:
        city = data.get('city')
        weight = data.get('weight')
        height = data.get('height')
        callories = data.get('callories')

        # Пример вывода информации
        response_message = (f"Город: {city}\n"
                            f"Вес: {weight}\n"
                            f"Рост: {height}\n"
                            f"Калории: {callories}")

        await message.reply(response_message)
    else:
        # Сообщение на случай, если данные недоступны
        await message.reply("Данные не найдены. Пожалуйста, заполните анкету заново.")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.reply(
        "Доступные команды:\n"
        "/log_water <количество> - Внести потребленную воду и посмотреть остаток до нормы\n"
        "/log_food <название продукта> - Сохраняет калорийность.\n"
        "/log_workout <тип тренировки> <время (мин)> - Фиксирует сожжённые калории.\n"
        "/check_progress - Прогресс по воде и калориям")


@router.message(Command("log_water"))
async def cmd_water(
        message: Message,
        command: CommandObject,
        state: FSMContext
):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
    data = await state.get_data()
    water_norm = int(data['water_norm'])
    if data['water_log'] is None:
        await state.update_data(water_log=int(command.args))
    else:
        water_new = int(data['water_log']) + int(command.args)
        await state.update_data(water_log=water_new)

    water_diff = water_norm - int(data['water_log'])
    if water_diff >0:
        await message.answer(f"До выполнения нормы осталось {water_diff} мл")
    else:
        await message.answer(f"Норма выполнена!")

# Функция для подключения обработчиков
def setup_handlers(dp):
    dp.include_router(router)