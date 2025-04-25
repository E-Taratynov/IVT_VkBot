from typing import Literal
import aiofiles
import json
from config import DataFiles

async def get_schedule_groups(filename='schedule_by_groups.json') -> list:
    groups = []
    async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
        content = await f.read()
    file = json.loads(content)
    for group in file:
        groups.append(group['group_name'])
    return groups
    

async def get_schedule_classrooms(filename='classrooms.json') -> list:
    classrooms = []
    async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
        content = await f.read()
    file = json.loads(content)
    for classroom in file:
        classrooms.append(classroom['classroom'])
    return classrooms
    

async def get_schedule_classrooms_session(filename='classrooms_session.json') -> list:
    classrooms = []
    async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
        content = await f.read()
    file = json.loads(content)
    for classroom in file:
        classrooms.append(classroom['classroom'])
    return classrooms

async def get_schedule_professors(filename='professors.json') -> list:
    professors = []
    async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
        content = await f.read()
    file = json.loads(content)
    for professor in file:
        professors.append(professor['professor'])
    return professors

async def get_formatted_output(filename: Literal[DataFiles.GROUPS, DataFiles.CLASSROOMS,
                                                 DataFiles.PROFESSORS],
                                                 search_str: str):
    async with aiofiles.open(filename.value, 'r', encoding='utf-8') as f:
        content = await f.read()
    file = json.loads(content)
    output = ''
    if filename == DataFiles.GROUPS:
        group_obj = next((obj for obj in file if obj.get('group_name') == search_str), None)
        if group_obj is None:
            return "Группа не найдена"
        subjects = group_obj['subjects']
        for day in subjects:
            output += day['day'] + '\n'
            day_str = ''
            for subject in day['subjects']:
                day_str += 'Пара:' + str(subject['class']) + ' '
                day_str += subject['subject']
                if subject['numerator'] == True:
                    day_str += ' - по числителю'
                elif subject['denominator'] == True:
                    day_str += ' - по знаменателю'
                day_str += '\n'
            output += day_str
        return output
    else:
        return 'Здесь будет форматированный вывод'
