
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware


from config import API_TOKEN

logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Создаем кнопки
def get_inline_keyboard():
    keyboard = InlineKeyboardMarkup()
    button1 = KeyboardButton("Подтвердить бронирование", callback_data='btn_1')
    button2 = InlineKeyboardButton("Посмотреть дополнительную информацию", callback_data='btn_2')
    button3 = InlineKeyboardButton("Отменить бронирование", callback_data='btn_3')
    keyboard.add(button1, button2, button3)
    return keyboard

# Обработчик для кнопки 1
@dp.callback_query_handler(lambda c: c.data == 'btn_1')
async def process_callback_btn1(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Бронирование для пользователя подтверждено", reply_markup=None)

# Обработчик для кнопки 2
@dp.callback_query_handler(lambda c: c.data == 'btn_2')
async def process_callback_btn2(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Здесь выводится информация об бронировании, номер телефона сколько было у пользователя броней и тд", reply_markup=None)

# Обработчик для кнопки 3
@dp.callback_query_handler(lambda c: c.data == 'btn_3')
async def process_callback_btn3(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Бронирование для пользователя отменено", reply_markup=None)
    # Показываем новое меню
    await bot.send_message(callback_query.from_user.id, "Выберите действие:", reply_markup=get_second_menu())

# Обработчик для кнопки "Позвонить клиенту"
@dp.callback_query_handler(lambda c: c.data == 'call_client')
async def process_call_client(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Пожалуйста, свяжитесь с клиентом по телефону.")

# Обработчик для кнопки "В главное меню"
@dp.callback_query_handler(lambda c: c.data == 'main_menu')
async def process_main_menu(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Вы вернулись в главное меню.", reply_markup=get_inline_keyboard())



def get_second_menu():
    keyboard = InlineKeyboardMarkup()
    call_client = InlineKeyboardButton("Позвонить клиенту", callback_data='call_client')
    main_menu = InlineKeyboardButton("В главное меню", callback_data='main_menu')
    keyboard.add(call_client, main_menu)
    return keyboard

# Функция отправки сообщения каждые 5 минут
async def send_message_every_5_minutes(user_id):
    while True:
        try:
            await bot.send_message(user_id, "Выберите вариант:", reply_markup=get_inline_keyboard())
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения: {e}")
        await asyncio.sleep(300)  # Задержка в 5 минут (300 секунд)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Бот отслеживание бронирования запущен. Вы будете получать сообщения о бронировании.")
    asyncio.create_task(send_message_every_5_minutes(message.from_user.id))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
