from vkbottle.bot import Bot, Message
from config import TOKEN

bot = Bot(token=TOKEN)

@bot.on.message()
async def echo(message: Message):
    await message.answer(message.text)

if __name__ == "__main__":
    bot.run_forever()