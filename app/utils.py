import aiofiles
import json

async def get_schedule_groups(filename='schedule_by_groups.json'):
    groups = []
    async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
        content = await f.read()
    file = json.loads(content)
    for group in file:
        groups.append(group['group_name'].replace('\n', ''))
    return groups
    

async def get_schedule_classrooms(filename='classrooms.json'):
    classrooms = []
    async with aiofiles.open(filename, 'r') as f:
        content = await f.read()
    file = json.loads(content)
    for classroom in file:
        classrooms.append(
            {
                'classroom': classroom['classroom'],
                'description': classroom['description']
            }
        )
    return classrooms
    

async def get_schedule_classrooms_session(filename='classrooms_session.json'):
    classrooms = []
    async with aiofiles.open(filename, 'r') as f:
        content = await f.read()
    file = json.loads(content)
    for classroom in file:
        classrooms.append(
            {
                'classroom': classroom['classroom'],
                'description': classroom['description']
            }
        )
    return classrooms

async def get_schedule_professors(filename='professors.json'):
    professors = []
    async with aiofiles.open(filename, 'r') as f:
        content = await f.read()
    file = json.loads(content)
    for professor in file:
        professors.append(professor['professor'])
    return professors

async def get_formatted_output():
    return 'Здесь будет форматированный вывод'