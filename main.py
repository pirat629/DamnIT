from aiogram import Bot,Dispatcher,executor,types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import re

TOKEN_API = '7007442319:AAFia58P8WwKSJABnGizTNbWtQZKx5TVwyU'
bot = Bot(TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Form(StatesGroup):
    name = State()
    number = State()
    comment = State()
    apply = State()

@dp.message_handler(commands = ["start"])
async def start(message: types.Message,state: FSMContext):
    await message.answer(text=f"{message.from_user.first_name} {message.from_user.last_name}, Добро пожаловать в компанию DamnIT")
    await Form.name.set()
    await message.answer("Напишите свое ФИО")
    await state.set_state(Form.name.state)

@dp.message_handler(state=Form.name)
async def set_name(message: types.Message, state: FSMContext):
    if message.text.count(' ') != 2 or any(ch.isdigit() for ch in message.text):
        await message.answer("Введено некорректрое ФИО. Пожалуйста повторите ввод")
        return
    await state.update_data(name = message.text)
    await state.set_state(Form.number.state)
    await message.answer("Укажите Ваш номер телефона")

@dp.message_handler(state=Form.number)
async def set_number(message: types.Message, state: FSMContext):
    result = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', message.text)
    if not result:
        await message.answer("Введенный номер телефона некорректен. Пожалуйста повторите ввод")
        return
    await state.update_data(number=message.text)
    await state.set_state(Form.comment.state)
    await message.answer("Напишите любой комментарий")

@dp.message_handler(state=Form.comment)
async def set_comm(message: types.Message, state: FSMContext):
    await state.update_data(comment = message.text)
    await message.answer("Последний шаг! Ознакомься с вводными положениями")
    await bot.send_document(message.chat.id,document=open("test.pdf","rb"))
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Да")
    await message.answer("Ознакомился?", reply_markup=keyboard)
    await state.set_state(Form.apply.state)

@dp.message_handler(state=Form.apply)
async def set_apply(message: types.Message, state: FSMContext):
    if message.text != "Да":
        await message.answer("Пожалуйста нажмите на кномку принять, если Вы ознакомились.")
        return
    await message.answer("Спасибо за успешную регистрацию",reply_markup=types.ReplyKeyboardRemove())
    await bot.send_photo(message.chat.id, photo=open("photo.jpg", "rb"))
    data = await state.get_data()
    await bot.send_message("6262559451", f"Пришла новая информация от {message.from_user.username}\n\
ФИО: {data['name']}\nТелефон: {data['number']}\nКомментарий: {data['comment']}")



if __name__ == "__main__":
    executor.start_polling(dp)