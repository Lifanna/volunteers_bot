from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


button1 = KeyboardButton('Отправить ссылки')
button2 = KeyboardButton('Рейтинг')
button3 = KeyboardButton('Профиль')
button4 = KeyboardButton('Задания')

menu_btns = ReplyKeyboardMarkup().row(
    button1, button2, button3, button4
)
