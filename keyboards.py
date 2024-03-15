from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


button1 = KeyboardButton('Отправить ссылки')
button2 = KeyboardButton('Рейтинг')
button3 = KeyboardButton('Профиль')
button4 = KeyboardButton('Задания')
button5 = KeyboardButton('Мои задания')

menu_btns = ReplyKeyboardMarkup().row(
    button1, button2, button3, button4, button5
)

SEND_LINK_BTN_OBJECT = InlineKeyboardButton('Отправить новую ссылку', callback_data="send_link")

SEND_LINK_BTN = InlineKeyboardMarkup().add(
    SEND_LINK_BTN_OBJECT
)

LOAD_MORE_BTN_OBJECT = InlineKeyboardButton('Загрузить еще', callback_data="load_more")

LOAD_MORE_BTN = InlineKeyboardMarkup().add(
    LOAD_MORE_BTN_OBJECT
)
