import os
from typing import Literal
import aiofiles
import json
from config import DataFiles

async def load_json(filename: str):
    """Загружает данные из файла .json, используя aiofiles

    Args:
        filename (str): Путь к файлу

    Returns:
        Прочитанный .json файл в виде python объекта 
    """
    async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
        content = await f.read()
        file = json.loads(content)
        return file


async def save_json(data, filename: str) -> None:
    """Сохраняет файл в формате .json

    Args:
        data (_type_): Данные для сохранения
        filename (str): Путь к сохраняемому файлу
    """
    async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
        json_data = json.dumps(data, ensure_ascii=False, indent=4)
        await f.write(json_data)

async def get_schedule_groups(filename: str = DataFiles.GROUPS.value) -> list:
    """Возвращает список доступных в расписании групп

    Args:
        filename (str, optional): Путь к файлу с расписанием по группам. Defaults to DataFiles.GROUPS.value.

    Returns:
        list: Список групп
    """
    groups = []
    file = await load_json(filename)
    for group in file:
        groups.append(group['group_name'])
    return groups
    

async def get_schedule_classrooms(filename: str = DataFiles.CLASSROOMS.value) -> list:
    """Возвращает список доступных в расписании аудиторий

    Args:
        filename (str, optional): Путь к файлу с расписанием по аудиториям. Defaults to DataFiles.CLASSROOMS.value.

    Returns:
        list: Список аудиторий
    """
    classrooms = []
    file = await load_json(filename)
    for classroom in file:
        classrooms.append(classroom['classroom'])
    return classrooms
    

async def get_schedule_professors(filename: str = DataFiles.PROFESSORS.value) -> list:
    """Возвращает список доступных в расписании преподавателей

    Args:
        filename (str, optional): Путь к файлу с расписанием по преподавателям. Defaults to DataFiles.PROFESSORS.value.

    Returns:
        list: Список преподавателей
    """
    professors = []
    file = await load_json(filename)
    for professor in file:
        professors.append(professor['professor'])
    return professors

def format_schedule(schedule_obj: dict) -> str:
    """Форматирует недельное расписание

    Args:
        schedule_obj (dict): Объект, соответствующий группе, аудитории, преподавателю

    Returns:
        str: Недельное расписание
    """
    result = []

    # Проходим по каждому дню недели
    for day_info in schedule_obj['subjects']:
        day = day_info['day']
        subjects = day_info['subjects']

        result.append(f"{day.capitalize()}:\n")

        # Создаем таблицу для текущего дня
        table = []
        current_class = None

        for subject in subjects:
            class_num = subject['class']
            subject_name = subject['subject'].strip().replace('\n', ' ')
            numerator = subject['numerator']
            denominator = subject['denominator']
            common = subject['common']

            if common:
                # Если предмет общий, добавляем его в таблицу
                table.append(f"{class_num}: {subject_name}")
            elif numerator:
                # Если предмет идет по числителю
                if current_class == class_num:
                    table[-1] += f" / {subject_name} (числитель)"
                else:
                    table.append(f"{class_num}: {subject_name} (числитель)")
                current_class = class_num
            elif denominator:
                # Если предмет идет по знаменателю
                if current_class == class_num:
                    table[-1] += f" / {subject_name} (знаменатель)"
                else:
                    table.append(f"{class_num}: {subject_name} (знаменатель)")
                current_class = class_num

        # Добавляем сформированную таблицу в результат
        result.append("\n".join(table) + "\n")

    return "\n".join(result)

async def get_formatted_output(filename: Literal[DataFiles.GROUPS, DataFiles.CLASSROOMS,
                                                 DataFiles.PROFESSORS],
                                                 search_str: str) -> str:
    """Возвращает форматированный вывод расписания

    Args:
        filename: Тип файла (группы, аудитории, преподаватели)
        search_str (str): Строка для поиска

    Returns:
        str: Форматированный вывод расписания
    """
    file = await load_json(filename.value)
    if filename == DataFiles.GROUPS:
        group_name = search_str
        group_obj = next((obj for obj in file if obj.get('group_name') == group_name), None)
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
    """Проверяет, зарегистрирован ли пользователь

    Args:
        user_id (int): Вк id пользователя
        users_file (str, optional): Путь к файлу с пользователями. Defaults to DataFiles.USERS_FILE.value.

    Returns:
        bool: 
    """
    if os.path.exists(users_file):
        users = await load_json(users_file)
        return str(user_id) in users.keys()
    return False

async def check_if_student_exists(student_id: str, students_file: str = DataFiles.STUDENTS_FILE.value) -> bool:
    """Проверяет, существует ли студент с данным номером билета

    Args:
        student_id (str): Номер студенческого билета
        students_file (str, optional): Путь к файлу с оценками. Defaults to DataFiles.STUDENTS_FILE.value.

    Returns:
        bool:
    """
    if os.path.exists(students_file):
        students = await load_json(students_file)
        return student_id in students.keys()
    return False

async def add_new_user(user_id: int, student_id: str, users_file: str = DataFiles.USERS_FILE.value) -> dict:
    """Добавляет нового пользователя

    Args:
        user_id (int): Вк id пользователя
        student_id (str): Номер студенческого билета
        users_file (str, optional): Путь к файлу с пользователями. Defaults to DataFiles.USERS_FILE.value.

    Returns:
        dict: Ответ в формате {'success': bool, 'text': str}
    """
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
    """Возвращает форматированный список оценок студента

    Args:
        user_id (int): Вк id пользователя
        users_file (str, optional): Путь к файлу с пользователями. Defaults to DataFiles.USERS_FILE.value.
        students_file (str, optional): Путь к файлу с оценками. Defaults to DataFiles.STUDENTS_FILE.value.

    Returns:
        str: Список оценок
    """
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
    """Удаляет пользователя

    Args:
        user_id (int): Вк id пользователя
        users_file (str, optional): Путь к файлу с пользователями. Defaults to DataFiles.USERS_FILE.value.

    Returns:
        dict: Ответ в формате {'success': bool, 'text': str}
    """
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
