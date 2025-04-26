from vkbottle.bot import Bot, Message, MessageEvent, rules
from vkbottle import GroupEventType, Keyboard, BaseStateGroup, Callback
from utils import (get_schedule_classrooms,
get_schedule_groups, get_schedule_professors, get_formatted_output, check_if_registered,
check_if_student_exists, get_student_marks_by_user_id, add_new_user, delete_user)
from config import TOKEN, DataFiles
import logging

bot = Bot(token=TOKEN)
logging.basicConfig(level=logging.INFO)

class MenuStates(BaseStateGroup):
    REGISTRATION_STATE = 'registration'
    HOME_STATE = 'home'
    UNREGISTERED_STATE = 'unregistered'
    REGISTERED_STATE = 'registered'
    GRADES_STATE = 'grades'
    SCHEDULE_STATE = 'schedule'
    SCHEDULE_STATE_GROUPS = 'schedule_groups'
    SCHEDULE_STATE_CLASSROOMS = 'schedule_classrooms'
    SCHEDULE_STATE_PROFESSORS = 'schedule_professors'

unregistered_keyboard = (
    Keyboard(one_time=False, inline=False)
    .add(Callback('Расписание', payload={'cmd': 'schedule', 'text': 'Расписание'}))
    .add(Callback('Регистрация', payload={'cmd': 'register', 'text': 'Регистрация'}))
)

home_keyboard = (
    Keyboard(one_time=False, inline=False)
    .add(Callback('Расписание', payload={'cmd': 'schedule', 'text': 'Расписание'}))
    .add(Callback('Мои оценки', payload={'state': 'grades', 'text': 'Мои оценки'}))
    .add(Callback('Отменить регистрацию', payload={'cmd': 'delete_user', 'text': 'Отменить регистрацию'}))
)

schedule_keyboard = (
    Keyboard(one_time=False, inline=False)
    .add(Callback('По группам', payload={'state': 'schedule_groups'}))
    .row()
    .add(Callback('По аудиториям', payload={'state': 'schedule_classrooms'}))
    .row()
    .add(Callback('По преподавателям', payload={'state': 'schedule_professors'}))
    .row()
    .add(Callback('Назад', payload={'cmd': 'return', 'text': 'Назад'}))
)

# Обработчик команды /start
@bot.on.message(command=('start'))
async def start(message: Message):
    if await check_if_registered(message.peer_id):
        await message.answer('Это бот ИВТ ЯрГУ.\nЗдесь вы можете узнать свои оценки и расписание занятий.',
                          keyboard=home_keyboard)
        await bot.state_dispenser.set(message.peer_id, MenuStates.HOME_STATE)
    else:
         await message.answer('Это бот ИВТ ЯрГУ.\nЗдесь вы можете узнать свои оценки и расписание занятий.',
                          keyboard=unregistered_keyboard)
         await bot.state_dispenser.set(message.peer_id, MenuStates.UNREGISTERED_STATE)

# Обработчик кнопки "Регистрация"
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent,
                  rules.PayloadContainsRule({'cmd': 'register'}))
async def registration_handler(event: MessageEvent):
    await event.send_message("Введите номер студенческого билета")
    await event.send_empty_answer()
    await bot.state_dispenser.set(event.peer_id, MenuStates.REGISTRATION_STATE)

# Обработчик ввода номера студенческого билета
@bot.on.message(state=MenuStates.REGISTRATION_STATE)
async def register_user(message: Message):
    student_id = message.text
    if await check_if_student_exists(student_id):
        response = await add_new_user(message.peer_id, student_id)
        if response['success']:
            await message.answer(response['text'], keyboard=home_keyboard)
            await bot.state_dispenser.set(message.peer_id, MenuStates.HOME_STATE)
        else:
            await message.answer(response['text'])
    else:
        await message.answer("Студента с данным номером билета не существует")

# Обработчик кнопки "Отменить регистрацию"
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent,
                  rules.PayloadContainsRule({'cmd': 'delete_user'}))
async def user_deletion_handler(event: MessageEvent):
    response = await delete_user(event.peer_id)
    if response['success']:
        await event.send_message(response['text'], keyboard=unregistered_keyboard)
        await bot.state_dispenser.set(event.peer_id, MenuStates.UNREGISTERED_STATE)
    else:
        await event.send_message(response['text'], keyboard=home_keyboard)
        await bot.state_dispenser.set(event.peer_id, MenuStates.HOME_STATE)
    await event.send_empty_answer()

# Обработчик кнопки "Расписание"    
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent, 
                  rules.PayloadContainsRule({'cmd': 'schedule'}))
async def schedule_handler(event: MessageEvent):
    await event.send_message(event.get_payload_json().get('text'), keyboard=schedule_keyboard)
    await event.send_empty_answer()
    await bot.state_dispenser.set(event.peer_id, MenuStates.SCHEDULE_STATE)

# Обработчик кнопки "Мои оценки"
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent,
                  rules.PayloadContainsRule({'state': 'grades'}))
async def grades_handler(event: MessageEvent):
    grades = await get_student_marks_by_user_id(event.peer_id)
    await event.send_message(grades)
    await event.send_empty_answer()
    await bot.state_dispenser.set(event.peer_id, MenuStates.GRADES_STATE)

# Обработчик кнопки "Назад"
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent,
                  rules.PayloadContainsRule({'cmd': 'return'}))
async def return_home(event: MessageEvent):
    if await check_if_registered(event.peer_id):
        await event.send_message(event.get_payload_json().get('text'), keyboard=home_keyboard)
        await bot.state_dispenser.set(event.peer_id, MenuStates.HOME_STATE)
    else:
        await event.send_message(event.get_payload_json().get('text'), keyboard=unregistered_keyboard)
        await bot.state_dispenser.set(event.peer_id, MenuStates.UNREGISTERED_STATE)
    await event.send_empty_answer()
    

# Обработчик кпопки "По группам"
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent,
                  rules.PayloadContainsRule({'state': 'schedule_groups'}))
async def show_groups(event: MessageEvent):
    groups = await get_schedule_groups()
    output = '\n'.join(groups)
    await event.send_message("Выберите группу:\n" + output)
    await event.send_empty_answer()
    await bot.state_dispenser.set(event.peer_id, MenuStates.SCHEDULE_STATE_GROUPS)

# Обработчик ввода группы
@bot.on.message(state=MenuStates.SCHEDULE_STATE_GROUPS)
async def get_schedule_by_group(message: Message):
    groups = await get_schedule_groups()
    if message.text in groups:
        await message.answer(await get_formatted_output(DataFiles.GROUPS, message.text))
    else:
        await message.answer('Группа не найдена')

# Обработчик кпопки "По аудиториям"
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent,
                  rules.PayloadContainsRule({'state': 'schedule_classrooms'}))
async def show_classrooms(event: MessageEvent):
    classrooms = await get_schedule_classrooms()
    output = '\n'.join(classrooms)
    await event.send_message("Выберите аудиторию:\n" + output)
    await event.send_empty_answer()
    await bot.state_dispenser.set(event.peer_id, MenuStates.SCHEDULE_STATE_CLASSROOMS)

# Обработчик ввода аудитории
@bot.on.message(state=MenuStates.SCHEDULE_STATE_CLASSROOMS)
async def get_schedule_by_classroom(message: Message):
    classrooms = await get_schedule_classrooms()
    if message.text in classrooms:
        await message.answer(await get_formatted_output())
    else:
        await message.answer('Аудитория не найдена')

# Обработчик кпопки "По преподавателям"
@bot.on.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent,
                  rules.PayloadContainsRule({'state': 'schedule_professors'}))
async def show_professors(event: MessageEvent):
    professors = await get_schedule_professors()
    output = '\n'.join(professors)
    await event.send_message("Выберите преподавателя:\n" + output)
    await event.send_empty_answer()
    await bot.state_dispenser.set(event.peer_id, MenuStates.SCHEDULE_STATE_PROFESSORS)

# Обработчик выбора преподавателя
@bot.on.message(state=MenuStates.SCHEDULE_STATE_PROFESSORS)
async def get_schedule_by_professor(message: Message):
    professors = await get_schedule_professors()
    if message.text in professors:
        await message.answer(await get_formatted_output())
    else:
        await message.answer('Преподаватель не найден')

# Ответ по умолчанию
@bot.on.message()
async def default(message: Message):
    await message.answer('Команда не распознана')


if __name__ == "__main__":
    bot.run_forever()