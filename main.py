import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import dotenv, os
from aiogram.dispatcher import FSMContext
from api import APIHandler
from aiogram.dispatcher.filters.state import State, StatesGroup
import keyboards
from aiogram.types import message as type_message
import asyncio, websockets, json
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import locale
from datetime import datetime


env = dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBSOCKET_URL = os.getenv('WEBSOCKET_URL')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class States(StatesGroup):
    init = State()
    send_link_init = State()
    send_link_state = State()


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    api_handler = APIHandler()
    result = api_handler.signin(message.from_user.id)

    if result:
        await message.answer(
            "Здравствуйте!\nВыберите действие",
            reply_markup=keyboards.menu_btns
        )
        await States.init.set()
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("Поделиться контактом", request_contact=True)
        keyboard.add(button)

        await message.answer("Пожалуйста, поделитесь своим контактом, нажав на кнопку ниже.", reply_markup=keyboard)


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contact_received(message: types.Message):
    contact = message.contact

    api_handler = APIHandler()
    result = api_handler.verify(message.from_user.id, contact.phone_number)

    if result:
        await message.answer(f"Спасибо за предоставленный контакт")
        await States.init.set()
    else:
        await message.answer(f"Пользователь не найден")


@dp.message_handler(lambda message: message.text.lower() == 'отправить ссылки', state=States.init)
async def process_start_command(message: types.Message, state: FSMContext):
    api_handler = APIHandler()
    user_links = api_handler.get_user_links(message.from_user.id)


    await message.answer("Мои ссылки")
    for user_link in user_links:
        await message.answer("%s\nСтатус: %s"%(user_link.get('link'), user_link.get('status')))

    await message.answer("Действия", reply_markup=keyboards.SEND_LINK_BTN)


@dp.callback_query_handler(text='send_link', state=States.init)
async def process_callback_button1(callback_query: types.CallbackQuery):
    await States.send_link_state.set()
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введите ссылку')


@dp.message_handler(state=States.send_link_state)
async def send_link(message: types.Message, state: FSMContext):
    link = message.text

    api_handler = APIHandler()
    result = api_handler.send_link(message.from_user.id, link)

    if result:
        await message.answer(f"Ссылка успешно отправлена, ожидайте подтверждения")
    else:
        await message.answer("Произошла ошибка!")

    await States.init.set()


@dp.message_handler(lambda message: message.text.lower() == 'рейтинг', state=States.init)
async def process_start_command(message: types.Message):
    api_handler = APIHandler()

    await message.answer("Рейтинг в работе")


@dp.message_handler(lambda message: message.text.lower() == 'профиль', state=States.init)
async def process_start_command(message: types.Message):
    api_handler = APIHandler()

    user_profile_text = api_handler.get_user_profile(str(message.from_user.id))

    await message.answer(user_profile_text)


@dp.message_handler(lambda message: message.text.lower() == 'задания', state=States.init)
async def process_start_command(message: types.Message):
    api_handler = APIHandler()
    tasks = api_handler.get_tasks(message.from_user.id)

    await message.answer("Список заданий")

    message_text = ""

    for task in tasks:
        task_kb = InlineKeyboardMarkup(row_width=1)
        task_buttons = InlineKeyboardButton(text="Принять к исполнению", callback_data=f"task_{task.get('id')}")
        task_kb.add(task_buttons)

        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

        # Преобразование строки в объект даты
        start_date_object = datetime.strptime(task.get('start_date'), '%Y-%m-%d')
        end_date_object = datetime.strptime(task.get('end_date'), '%Y-%m-%d')

        # Форматирование объекта даты в нужный формат с русскими названиями месяцев
        formatted__start_date = start_date_object.strftime('%d %B %Y')
        formatted__end_date = end_date_object.strftime('%d %B %Y')

        message_text = "Задание #%s\n%s\nОчков за задание:\n*%s*\nБрифинг:\n%s\nНачало:\n%s\nЗавершение:\n%s\n"\
            %(task.get('id'), task.get('name'), task.get('score'), task.get('text'), formatted__start_date, formatted__end_date)

        await bot.send_message(message.from_user.id, message_text, reply_markup=task_kb, parse_mode= 'Markdown')


async def send_data_via_websocket(data):
    async with websockets.connect(WEBSOCKET_URL + '/ws/') as websocket:
        await websocket.send(data)


@dp.callback_query_handler(lambda query: query.data.startswith('task_'))
async def execute_task_callback(query: types.CallbackQuery):
    task_id = query.data.split('_')[1]

    data_to_send = {
        "user": str(query.from_user.id),
        "task_id": str(task_id)
    }

    await send_data_via_websocket(json.dumps(data_to_send))


async def send_telegram_message(user_id, message_text):
    try:
        await bot.send_message(user_id, message_text)
        print(f"Message sent to user {user_id}: {message_text}")
    except Exception as e:
        print(f"Failed to send message to user {user_id}: {e}")


async def process_message_task_status_create(data):
    print(f"Received data: {data}")

    task = data.get("task")
    users = data.get("users")

    if task and users:
        asyncio.create_task(send_message_task_status_create(task, users, "Новое задание:"))


async def send_message_task_status_create(task, users, message_text):
    task_kb = InlineKeyboardMarkup(row_width=1)
    task_buttons = InlineKeyboardButton(text="Принять к исполнению", callback_data=f"task_{task['task_id']}")
    task_kb.add(task_buttons)

    message_text += "\n%s\nОчков за задание:\n%s\nБрифинг:\n%s\nНачало:\n%s\nЗавершение:\n%s\n"\
        %(task['task_name'], task['score'], task['text'], task['start_date'], task['end_date'])

    for user_id in users:
        print(user_id)
        await bot.send_message(user_id, message_text, reply_markup=task_kb)

        print(f"Message sent to user {user_id}: {message_text}")


async def send_message_user_task_created(user_id, message_text):
    try:
        await bot.send_message(user_id, message_text)

        print(f"Message sent to user {user_id}: {message_text}")
    except Exception as e:
        print(f"Failed to send message to user {user_id}: {e}")


async def process_message_user_task_created(data):
    print(f"Received data: {data}")

    user_id = data.get("user")
    if user_id:
        asyncio.create_task(send_message_user_task_created(user_id, "Задание принято к исполнению!"))


async def receive_data():
    try:
        async with websockets.connect(WEBSOCKET_URL + '/ws/') as websocket:
            print("Connected to WebSocket server")
            async for message in websocket:
                data = json.loads(message)

                action = data.get('payload').get('action')
                payload = data.get('payload')

                if action == 'task_status_create':
                    await process_message_task_status_create(payload)
                elif action == 'user_task_created':
                    await process_message_user_task_created(payload)
    except websockets.exceptions.WebSocketException as e:
        print(f"WebSocket connection error: {e}")


async def start_bot():
    event_loop.create_task(dp.start_polling())


if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(receive_data())
    event_loop.run_until_complete(start_bot())
    event_loop.run_forever()
