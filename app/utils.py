import os
from typing import Literal
import aiofiles
import json
from config import DataFiles

async def get_schedule_groups(filename='schedule_by_groups.json') -> list:
    groups = []
    file = await load_json(filename)
    for group in file:
        groups.append(group['group_name'])
    return groups
    

async def get_schedule_classrooms(filename='classrooms.json') -> list:
    classrooms = []
    file = await load_json(filename)
    for classroom in file:
        classrooms.append(classroom['classroom'])
    return classrooms
    

async def get_schedule_classrooms_session(filename='classrooms_session.json') -> list:
    classrooms = []
    file = await load_json(filename)
    for classroom in file:
        classrooms.append(classroom['classroom'])
    return classrooms

async def get_schedule_professors(filename='professors.json') -> list:
    professors = []
    file = await load_json(filename)
    for professor in file:
        professors.append(professor['professor'])
    return professors

async def get_formatted_output(filename: Literal[DataFiles.GROUPS, DataFiles.CLASSROOMS,
                                                 DataFiles.PROFESSORS],
                                                 search_str: str) -> str:
    file = load_json(filename.value)
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

async def load_json(filename: str):
    """
    Загружает данные из файла .json

    :param filename: Путь к файлу
    :return: Данные из .json
    """
    async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
        content = await f.read()
        file = json.loads(content)
        return file


async def save_json(data, filename: str) -> None:
    """
    Сохраняет данные в файле .json

    :param data: Данные, которые надо сохранить
    :param filename: Путь к файлу
    :return:
    """
    async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        await f.write(json_data)

async def check_if_registered(user_id: int, users_file: str = DataFiles.USERS_FILE.value) -> bool:
    if os.path.exists(users_file):
        users = await load_json(users_file)
        return str(user_id) in users.keys()
    return False

async def check_if_student_exists(student_id: str, students_file: str = DataFiles.STUDENTS_FILE.value) -> bool:
    if os.path.exists(students_file):
        students = await load_json(students_file)
        return student_id in students.keys()
    return False

async def add_new_user(user_id: int, student_id: str, users_file: str = DataFiles.USERS_FILE.value):
    if os.path.exists(users_file):
        users = await load_json(users_file)
    else:
        users = {}
    users[str(user_id)] = student_id
    await save_json(users, users_file)

async def get_student_marks_by_user_id(user_id: int, users_file: str = DataFiles.USERS_FILE.value,
                                       students_file: str = DataFiles.STUDENTS_FILE.value) -> str:
    if os.path.exists(students_file) and os.path.exists(users_file):
        students = await load_json(students_file)
        users = await load_json(users_file)
    else:
        return "Оценки не найдены"
    
    try:
        student_id = users[str(user_id)]
        grades_dict = students[student_id]
    except KeyError:
        return 'Пользователь не найден'
    grades_str = '\n'.join(f"{key}: {value}" for key, value in grades_dict.items())
    return grades_str