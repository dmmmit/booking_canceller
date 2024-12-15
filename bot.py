import logging
import asyncio
import pandas as pd
import joblib
from io import BytesIO

from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware

HELP_COMMAND = '''
/start - начать работу
/help - список команд
'''

from config import API_TOKEN

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_start = KeyboardButton("/start")
button_help = KeyboardButton("/help")
current_index = 0  
is_processing = False 




def get_main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton("Профиль отеля")
    button2 = KeyboardButton("Статистика по отелю")
    keyboard.add(button1, button2)
    return keyboard


def get_reply_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    button1 = KeyboardButton("Подтвердить бронирование")
    button2 = KeyboardButton("Посмотреть дополнительную информацию")
    button3 = KeyboardButton("Отменить бронирование")

    keyboard.add(button1, button3)
    keyboard.add(button2)

    return keyboard


def get_reply_keyboard_without_dopinfo():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button1 = KeyboardButton("Подтвердить бронирование")
    button3 = KeyboardButton("Отменить бронирование")
    keyboard.add(button1, button3)
    return keyboard


def get_second_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_call_client = KeyboardButton("Позвонить клиенту")
    button_main_menu = KeyboardButton("В главное меню")
    keyboard.add(button_call_client, button_main_menu)
    return keyboard


def get_third_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_main_menu = KeyboardButton("В главное меню")
    keyboard.add(button_main_menu)
    return keyboard
def get_user_info(user_id):
    return {
        'Имя': 'Иван',
        'Телефон': '+7-999-999-99-99',
        'Email': 'ivan@mail.ru'}


def get_full_stat():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_main_menu = KeyboardButton("В главное меню")
    button_graph = KeyboardButton("Графики")
    button_dop1 = KeyboardButton("По региону")
    button_dop2 = KeyboardButton("Список бронь")

    keyboard.add(button_main_menu, button_graph, button_dop1, button_dop2)
    return keyboard


@dp.message_handler(lambda message: message.text == "Профиль отеля")
async def process_profile(message: types.Message):
    await message.reply("Гостиница: Hotel Group Cosmoc MSK. Рейтинг: 4.87", reply_markup=get_main_menu())


@dp.message_handler(lambda message: message.text == "Статистика по отелю")
async def process_statistics(message: types.Message):
    await message.reply("Статистика по отелю: 75% бронирований, 20% отменено, 5% не подтверждено",
                        reply_markup=get_full_stat())


@dp.message_handler(lambda message: message.text == "Графики")
async def process_statistics(message: types.Message):
    await message.reply("Подробная информация в графиках:", reply_markup=get_main_menu())


@dp.message_handler(lambda message: message.text == "доп1")
async def process_statistics(message: types.Message):
    await message.reply("Дополнительная информация 1", reply_markup=get_main_menu())


@dp.message_handler(lambda message: message.text == "доп2")
async def process_statistics(message: types.Message):
    await message.reply("Дополнительная информация 2", reply_markup=get_main_menu())


@dp.message_handler(lambda message: message.text == "Подтвердить бронь")
async def process_booking_confirm(message: types.Message):
    global booking_allowed
    booking_allowed = False 
    await message.reply("Бронь подтверждена.")
    booking_allowed = True  




@dp.message_handler(lambda message: message.text == "Посмотреть дополнительную информацию")
async def process_view_info(message: types.Message):
    user_info = get_user_info(message.from_user.id)  
    if user_info:
        await message.reply(
            f"Имя: {user_info['Имя']}, Телефон: {user_info['Телефон']}, Email: {user_info['Email']}",
            reply_markup=get_reply_keyboard_without_dopinfo()
        )
    else:
        await message.reply(
            "Информация о пользователе не найдена.",
            reply_markup=get_reply_keyboard_without_dopinfo()
        )



@dp.message_handler(lambda message: message.text == "Отменить бронь")
async def process_booking_cancel(message: types.Message):
    global booking_allowed
    booking_allowed = False  
    await message.reply("Бронь отменена.")
    booking_allowed = True  


@dp.message_handler(lambda message: message.text == "Позвонить клиенту")
async def process_call_client(message: types.Message):
    await message.reply("Пожалуйста, свяжитесь с клиентом по телефону.", reply_markup=get_third_menu())


@dp.message_handler(lambda message: message.text == "В главное меню")
async def process_main_menu(message: types.Message):
    await message.reply("Вы вернулись в главное меню.", reply_markup=get_reply_keyboard())


def get_next_row():
    data = pd.read_csv('data/test_with_name.csv')
    global current_index
    if current_index < len(data):
        row = data.iloc[current_index]
        user_info = {
            'Имя': row['Имя'],
            'Телефон': row['Телефон'],
            'Email': row['Email']
        }
        current_index += 1
        return row.drop(['Имя', 'Телефон', 'Email']).values.reshape(1, -1), user_info
    else:
        return None, None  



async def model_predict(row):
    loaded_model = joblib.load('random_forest_model.pkl')
    prediction = loaded_model.predict_proba(row)[:, 1][0].round(2)
    return f"Бронь отменится с вероятностью: {prediction}"


async def new_booking(user_id):
    while True:
        try:
            if booking_allowed: 
                row, user_info = get_next_row()
                if row is not None:
                    prediction = await model_predict(row)
                    await bot.send_message(user_id, f"Поступила новая бронь: {prediction}")

                    user_message = f"Имя: {user_info['Имя']}, Телефон: {user_info['Телефон']}, Email: {user_info['Email']}"
                    await bot.send_message(user_id, user_message, reply_markup=get_reply_keyboard())
                else:
                    logging.info("Строки закончились.")
            else:
                logging.info("Получение новых бронирований приостановлено.")

        except Exception as e:
            logging.error(f"Ошибка отправки сообщения: {e}")
        await asyncio.sleep(120)  


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Бот отслеживания бронирования запущен. Вы будете получать сообщения о бронировании.",
                           reply_markup=get_main_menu(), parse_mode='HTML')
    asyncio.create_task(new_booking(message.from_user.id))


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply(text=HELP_COMMAND)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
