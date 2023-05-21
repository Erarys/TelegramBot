from aiogram import Bot, Dispatcher, F, types
from aiogram.enums.dice_emoji import DiceEmoji
from aiogram.filters import Command, CommandObject, Text
from aiogram.types import BufferedInputFile, FSInputFile
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from config_reader import config
import json
import time
import os
import asyncio

bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"<b>Пользователь привет!</b> 😁")

    kb = [[types.KeyboardButton(text="возможности"), types.KeyboardButton(text="спец возможности")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer_photo(FSInputFile("emo/hi.jpeg"), reply_markup=keyboard)


@dp.message(Text("спец возможности"))
async def special_option(message: types.Message):
    builder = ReplyKeyboardBuilder()

    builder.row(
        types.KeyboardButton(text="Геолокация", request_location=True),
        types.KeyboardButton(text="Контакты", request_contact=True)
    )
    builder.row(
        types.KeyboardButton(text="Опрос", request_poll=types.KeyboardButtonPollType(type="survey")),
        types.KeyboardButton(text="Викторины", request_poll=types.KeyboardButtonPollType(type="quiz"))
    )

    await message.answer("<b>Выберите опцию:</b>", reply_markup=builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    ),
                         parse_mode="HTML"
                         )


@dp.message(Text("возможности"))
async def option(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="/motivation"),
            types.KeyboardButton(text="/calculate"),
            types.KeyboardButton(text="/dice")
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите"
    )
    await message.answer("Вот что я могу:", reply_markup=keyboard)


@dp.message(Command("dice"))
async def cmd_dice(message: types.Message):
    builder = ReplyKeyboardBuilder()
    for i in range(1, 7):
        builder.add(types.KeyboardButton(text=i))

    builder.adjust(3)
    await message.answer(
        "Выберите:",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )


@dp.message(lambda message: message.text in map(str, range(1, 7)))
async def check(message: types.Message):
    result = await message.answer_dice(emoji=DiceEmoji.DICE)
    time.sleep(4)
    if result.dice.value == int(message.text):
        await message.reply("Вы угадали")
    else:
        await message.reply("Вы не угадали")
    await message.answer("{} - {}".format(message.text, result.dice.value))


@dp.message(Command("calculate"))
async def cmd_calculate(message: types.Message, command: CommandObject):
    try:
        await message.answer(eval(command.args))
    except Exception as exc:
        await message.answer(f"Ошибка {exc}")


@dp.message(Command("motivation"))
async def cmd_motivation(message: types.Message):
    if cmd_motivation.count <= len(os.listdir("img/")):
        await message.answer_photo(
            FSInputFile(f"img/m{cmd_motivation.count}.jpeg"),
            caption="Еще? /motivation"
        )
        cmd_motivation.count += 1
    else:
        await message.reply("На сегодня все!")


cmd_motivation.count = 1


@dp.message(F.contact)
async def get_number(message: types.Message):
    with open("users.json", "r+") as users:
        json.dump(message.contact.dict(), users, indent=4)

        users.seek(0)
        await message.answer("Вот ваши данные: \n{}".format(
            "\n".join(map(lambda t: str(t).strip("()"), json.load(users).items()))
        ))


@dp.message(F.photo)
async def add_photo(message: types.Message, bot: Bot):
    add_photo.count += 1
    await bot.download(message.photo[-1], f"img/m{add_photo.count}.jpeg")
    await message.answer("Ваша фотография сохранена")


add_photo.count = len(os.listdir("img/"))


@dp.message(F.text)
async def cmd_message(message: types.Message):
    data = {}
    for item in message.entities or []:
        data[item.type] = item.extract_from(message.text)

    if data is {}:
        await message.answer(str(data))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
