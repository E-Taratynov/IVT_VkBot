from vkbottle.bot import Bot, Message, MessageEvent, rules
from vkbottle import GroupEventType, Keyboard, BaseStateGroup, Callback
from utils import (get_schedule_classrooms, get_schedule_classrooms_session,
get_schedule_groups, get_schedule_professors, get_formatted_output)
from config import TOKEN

bot = Bot(token=TOKEN)

class MenuStates(BaseStateGroup):
    HOME_STATE = 'home'
    UNREGISTERED_STATE = 'unregistered'
    REGISTERED_STATE = 'registered'
    GRADE_STATE = 'grades'
    SCHEDULE_STATE = 'schedule'
    SCHEDULE_STATE_GROUPS = 'schedule_groups'
    SCHEDULE_STATE_CLASSROOMS = 'schedule_classrooms'
    SCHEDULE_STATE_CLASSROOMS_SESSION = 'schedule_classrooms_session'
    SCHEDULE_STATE_PROFESSORS = 'schedule_professors'

unregistered_keyboard = (
    Keyboard(one_time=False, inline=False)
    .add(Callback('Расписание', payload={'cmd': 'schedule', 'text': 'Расписание'}))
    .add(Callback('Регистрация', payload={'cmd': 'register'}))
)

home_keyboard = (
    Keyboard(one_time=False, inline=False)
    .add(Callback('Расписание', payload={'cmd': 'schedule', 'text': 'Расписание'}))
    .add(Callback('Мои оценки', payload={'state': 'grades'}))
)

schedule_keyboard = (
    Keyboard(one_time=False, inline=False)
    .add(Callback('По группам', payload={'state': 'schedule_groups', 'text': 'По группам'}))
    .row()
    .add(Callback('По аудиториям', payload={'state': 'schedule_classrooms'}))
    .row()
    .add(Callback('По аудиториям - сессия, предзащиты', payload={'state': 'schedule_classrooms_session'}))
    .row()
    .add(Callback('По преподавателям', payload={'state': 'schedule_professors'}))
    .row()
    .add(Callback('Назад', payload={'state': 'home'}))
)

@bot.on.message(command=('start'))
async def start(message: Message):
    await message.answer('Это бот ИВТ ЯрГУ.\nЗдесь вы можете узнать свои оценки и расписание занятий.',
                          keyboard=home_keyboard)
    await bot.state_dispenser.set(message.peer_id, MenuStates.HOME_STATE)
    
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, 
                  rules.PayloadContainsRule({'cmd': 'schedule'}))
async def schedule_handler(event: MessageEvent):
    await event.send_message(event.get_payload_json().get('text'), keyboard=schedule_keyboard)
    await event.send_empty_answer()
    await bot.state_dispenser.set(event.peer_id, MenuStates.SCHEDULE_STATE)

@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent,
                  rules.PayloadContainsRule({'state': 'schedule_groups'}))
async def show_groups(event: MessageEvent):
    groups = await get_schedule_groups()
    output = '\n'.join(groups)
    await event.send_message("Введите группу:\n" + output)
    await event.send_empty_answer()
    await bot.state_dispenser.set(event.peer_id, MenuStates.SCHEDULE_STATE_GROUPS)

@bot.on.message(state=MenuStates.SCHEDULE_STATE_GROUPS)
async def get_schedule_by_groups(message: Message):
    groups = await get_schedule_groups()
    if message.text in groups:
        await message.answer(await get_formatted_output())
    else:
        await message.answer('Группа не найдена')

# Ответ по умолчанию
@bot.on.message()
async def default(message: Message):
    await message.answer('Команда не распознана')


if __name__ == "__main__":
    bot.run_forever()