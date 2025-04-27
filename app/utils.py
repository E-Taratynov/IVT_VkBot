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
    if filename == DataFiles.GROUPS:
        group_obj = next((obj for obj in file if obj.get('group_name') == search_str), None)
        if group_obj is None:
            return "Группа не найдена"
        
        return format_week_schedule(group_obj)
    else:
        return 'Здесь будет форматированный вывод'
    
    if filename == DataFiles.CLASSROOMS:
        classroom_obj = next((obj for obj in file if obj.get('classroom') == search_str), None)
        if classroom_obj is None:
            return "Аудитория не найдена"
        
        return format_classroom_schedule(classroom_obj)
    else:
        return 'Здесь будет форматированный вывод'

    if filename == DataFiles.PROFESSORS:
        professor_obj = next((obj for obj in file if obj.get('professor') == search_str), None)
        if professor_obj is None:
            return "Преподаватель не найден"
        
        return format_professor_schedule(professor_obj)
    else:
        return 'Здесь будет форматированный вывод'


def format_week_schedule(group_obj: dict) -> str:
    subjects = group_obj['subjects']
    result = [f"Расписание на неделю:\n"]

    for day in subjects:
        day_name = day["day"].capitalize()

        classes = {}
        for subject in day["subjects"]:
            class_num = subject["class"]
            if class_num not in classes:
                classes[class_num] = {"common": None, "numerator": None, "denominator": None}
            if subject["common"]:
                classes[class_num]["common"] = subject["subject"]
            elif subject["numerator"]:
                classes[class_num]["numerator"] = subject["subject"]
            elif subject["denominator"]:
                classes[class_num]["denominator"] = subject["subject"]

        result.append(f"\U0001F4C5 {day_name}")
        if not classes:
            result.append(f"\U0000274C Нет пар\n")
            continue

        for class_num in sorted(classes.keys()):
            entry = classes[class_num]
            pair_label = f"{class_num} пара"
            if entry["common"]:
                result.append(f"{pair_label} — {entry['common']}")
            else:
                result.append(f"{pair_label}:\n"
                            f"\U0001F538Числитель — {entry['numerator'] or 'Нет пары'}\n"
                            f"\U0001F539Знаменатель — {entry['denominator'] or 'Нет пары'}")

        result.append("")  

    return "\n".join(result)

def format_classroom_schedule(classroom_data: dict) -> str:
    result = [f"\U0001F4C5 Расписание аудитории {classroom_data['classroom']}:"]
    result.append(f"\U0001F5A5 {classroom_data['description']}\n")

    for day in classroom_data['subjects']:
        day_name = day['day'].capitalize()
        schedules = day['subjects']

        result.append(f"\U0001F4C5 {day_name}:")

        for schedule in schedules:
            subject = schedule['subject']
            class_num = schedule['class']
            if subject != "-": 
                result.append(f"{class_num} пара — {subject}")

        result.append("") 

    return "\n".join(result)

def format_professor_schedule(week_data: dict) -> str:
    professor = week_data["professor"]
    days = week_data["subjects"]
    result = [f"Расписание на неделю для {professor}:\n"]

    for day in days:
        day_name = day["day"].capitalize()
        subjects = day["subjects"]

        if not any(subject["subject"] not in ["-", ""] for subject in subjects):
            continue  
     
        classes = {}
        for item in subjects:
            class_num = item["class"]
            if class_num not in classes:
                classes[class_num] = {"common": None, "numerator": None, "denominator": None}
            if item["common"]:
                classes[class_num]["common"] = item["subject"]
            elif item["numerator"]:
                classes[class_num]["numerator"] = item["subject"]
            elif item["denominator"]:
                classes[class_num]["denominator"] = item["subject"]

        result.append(f"\U0001F4C5 {day_name}")
        if not classes:
            result.append(f"\U0000274C Нет пар\n")
            continue

        for class_num in sorted(classes.keys()):
            entry = classes[class_num]
            pair_label = f"{class_num} пара"
            if entry["common"]:
                result.append(f"{pair_label} — {entry['common']}")
            else:
                result.append(f"{pair_label}:\n"
                              f"\U0001F538Числитель — {entry['numerator'] or 'Нет пары'}\n"
                              f"\U0001F539Знаменатель — {entry['denominator'] or 'Нет пары'}")

        result.append("")  

    return "\n".join(result)

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

async def add_new_user(user_id: int, student_id: str, users_file: str = DataFiles.USERS_FILE.value) -> dict:
    if os.path.exists(users_file):
        users = await load_json(users_file)
    else:
        users = {}
    if student_id in users.values():
        return {
            'success': False,
            'text': 'Данный пользователь уже зарегистрирован'
        }
    users[str(user_id)] = student_id
    await save_json(users, users_file)
    return {
            'success': True,
            'text': 'Успешная регистрация'
        }

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

async def delete_user(user_id: int, users_file: str = DataFiles.USERS_FILE.value) -> dict:
    if os.path.exists(users_file):
        users = await load_json(users_file)
    else:
        return {
            'success': False,
            'text': 'Пользователь не найден'
        }
    try:
        student_id = users.pop(str(user_id))
        await save_json(users, users_file)
        return {
            'success': True,
            'text': f'Данные студента {student_id} удалены'
        }
    except KeyError:
        return {
            'success': False,
            'text': 'Пользователь не найден'
        }
    except Exception:
        return {
            'success': False,
            'text': 'Произошла ошибка'
        }