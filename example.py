from os import getenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv
from aiogram.utils import executor
from api import API
import kb  # Импортируйте модуль kb, если он содержит клавиатуры
from aiogram.types import CallbackQuery
from aiogram.utils import exceptions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
 
load_dotenv()
# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("BOT_TOKEN")
# All handlers should be attached to the Router (or Dispatcher)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!", reply_markup=kb.greet_kb)

@dp.message_handler(lambda message: message.text == 'Привет! 👋')
async def process_hi_button_click(message: types.Message):
    # Здесь можете добавить логику для вывода категорий
    await message.reply("Выберите категорию:", reply_markup=kb.categories_kb)

@dp.callback_query_handler(lambda query: query.data.startswith('category_'))
async def process_category_callback(query: CallbackQuery):
    category = query.data  # Получаем данные выбранной категории

    if category == 'category_1':
        api = API()
        books = api.get_books_list()  # Получаем список книг из вашего API
        books_kb = InlineKeyboardMarkup(row_width=1)

        # Создаем кнопки для каждой книги в списке
        book_buttons = [
            InlineKeyboardButton(text=book['bookname'], callback_data=f"book_{book['id']}")
            for book in books
        ]
        
        # Добавляем кнопки книг в клавиатуру
        books_kb.add(*book_buttons)
        
        try:
            # Отправляем новую клавиатуру пользователю
            await query.message.edit_reply_markup(reply_markup=books_kb)
        except exceptions.MessageNotModified:
            pass
    else:
        # Ваша логика для других категорий
        pass


 
from websocket import create_connection
 
# Функция для отправки данных по WebSocket
def send_data_via_websocket(data):
    ws = create_connection("ws://10.100.2.12:8000/ws/")
    ws.send(data)
    result = ws.recv()
    ws.close()
    return result
 
   
import asyncio
import websockets
 
# async def receive_data():
#     async with websockets.connect('ws://10.100.2.12:8000/ws/') as websocket:
#         while True:
#             data = await websocket.recv()  # Получение данных из вебсокета
#             print(f"Полученные данные: {data}")  # Обработка полученных данных


 
# Определяем асинхронную функцию отправки данных по WebSocket
async def send_data_via_websocket(data):
    async with websockets.connect('ws://10.100.2.12:8000/ws/') as websocket:
        await websocket.send(data)  # Отправляем данные по веб-сокету
 
@dp.callback_query_handler(lambda query: query.data.startswith('book_'))
async def process_book_callback(query: CallbackQuery):
    book_id = query.data.split('_')[1]  # Получаем ID книги из данных callback-запроса
    api = API()
    book_info = api.get_book_info(book_id)  # Получаем информацию о книге по ID
    # Создаем кнопку с ID книги
    book_id_button = InlineKeyboardButton(text=f"Купить книгу : {book_info['bookname']}", callback_data='dummy_data')
    
    # Создаем клавиатуру с кнопкой ID книги
    book_id_kb = InlineKeyboardMarkup().add(book_id_button)
   
  
    await query.message.reply(
        f"Автор: {book_info['author']}\nЦена: {book_info['price']}",
        reply_markup=book_id_kb
    )
      
    # После нажатия кнопки "Купить" отправляем данные по WebSocket
    data_to_send = {
        "user": str(query.from_user.id),
        "id": str(book_info['id'])
    } 
    import json
    await send_data_via_websocket(json.dumps(data_to_send))  # Ожидаем завершения отправки данных
 
# Теперь сначала запустим функцию receive_data() для получения данных
async def receive_data():
    async with websockets.connect('ws://10.100.2.12:8000/ws/') as websocket:
        while True:
            data = await websocket.recv()  # Получение данных из вебсокета
            print(f"Полученные данные: {data}")  # Обработка полученных данных

 
import json


 
async def receive_data():
    try:
        async with websockets.connect('ws://10.100.2.12:8000/ws/') as websocket:
            print("Connected to WebSocket server")
            async for message in websocket:
                data = json.loads(message)
                print("sadsad",data)
                await process_message(data)
    except websockets.exceptions.WebSocketException as e:
        print(f"WebSocket connection error: {e}")
 
async def send_telegram_message(user_id, message_text):
    try:
        await bot.send_message(user_id, message_text)
        print(f"Message sent to user {user_id}: {message_text}")
    except Exception as e:
        print(f"Failed to send message to user {user_id}: {e}")
 
def process_message(data):
    print(f"Received data: {data}")
    # Ваша логика обработки данных из WebSocket
    user_id = data.get("user_id")
    payment_id = data.get("payment_id")
    if user_id:
        # Отправка сообщения пользователю в Telegram
        asyncio.create_task(send_telegram_message(user_id, "Ваш заказ обработан\nНомер вашего заказа %s"%payment_id))
 
import asyncio
 
async def start_bot():
    event_loop.create_task(dp.start_polling())
    
if __name__ == '__main__':
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(receive_data())
    event_loop.run_until_complete(start_bot())
    event_loop.run_forever()
