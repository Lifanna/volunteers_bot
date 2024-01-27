import logging
from aiogram import Bot, Dispatcher, executor, types
import dotenv, os
from api import APIHandler
import keyboards
from aiogram.types import message as type_message

env = dotenv.load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    # await message.answer(
    #     "Здравствуйте!\nВведите свой номер телефона",
    #     reply_markup=keyboards.menu_btns
    # )
    await message.answer(
        "Здравствуйте!",
        reply_markup=types.ReplyKeyboardRemove()
    )

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Поделиться контактом", request_contact=True)
    keyboard.add(button)

    await message.answer("Пожалуйста, поделитесь своим контактом, нажав на кнопку ниже.", reply_markup=keyboard)


@dp.message_handler(content_types=types.ContentType.CONTACT)
async def contact_received(message: types.Message):
    contact = message.contact
    await message.answer(f"Спасибо за предоставленный контакт: {contact.first_name} {contact.last_name}, {contact.phone_number}")


@dp.message_handler(lambda message: message.text == 'Отправить ссылки')
async def process_start_command(message: types.Message):
    api_handler = APIHandler()

    await message.answer("Отправить ссылки в работе")


@dp.message_handler(lambda message: message.text == 'Рейтинг')
async def process_start_command(message: types.Message):
    api_handler = APIHandler()

    await message.answer("Рейтинг в работе")


@dp.message_handler(lambda message: message.text == 'Профиль')
async def process_start_command(message: types.Message):
    api_handler = APIHandler()

    user_profile = api_handler.get_user_profile(str(message.from_user.id))

    response = "Произошла ошибка"

    if user_profile != {}:
        response = "Имя:" + user_profile.get('first_name') + "\n" \
        "Фамилия:" + user_profile.get('last_name') + "\n" \
        "Направление:" + user_profile.get('direction') + "\n" \
        "Количество ссылок за все время:" + user_profile.get('total_links') + "\n" \
        "Подтвержденные за все время:" + user_profile.get('total_approved') + "\n" \
        "Подтвержденные за текущий месяц:" + user_profile.get('total_approved_current_month') + "\n"

        await message.answer(response)
    else:
        await message.answer(response)


@dp.message_handler(lambda message: message.text == 'Задания')
async def process_start_command(message: types.Message):
    api_handler = APIHandler()

    await message.answer("Задания в работе")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
