from aiogram import types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз! Нажмите «Начать игру» или введите /quiz", reply_markup=builder.as_markup(resize_keyboard=True))
