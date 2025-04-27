import os
from dotenv import load_dotenv
from enum import Enum


# Enum для путей к файлам
class DataFiles(Enum):
    SCHEDULE_FILE = 'schedule_file.xlsx'
    USERS_FILE = 'users.json'
    STUDENTS_FILE = 'students.json'
    GROUPS = 'schedule_by_groups.json'
    CLASSROOMS = 'classrooms.json'
    PROFESSORS = 'professors.json'

# Загрузка переменных окружения из файла .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
dotenv_path = os.path.normpath(dotenv_path)
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# API Яндекс диска
API_URL = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
# Токен бота
TOKEN = os.getenv("TOKEN")
# Ссылка на таблицу с расписанием в формате "https://docs.google.com/spreadsheets/d/*id*/..."
GOOGLE_DRIVE_URL = os.getenv("GOOGLE_DRIVE_URL")
# Ссылка на Яндекс диск с оценками в формате "https://disk.yandex.ru/*id*"
YANDEX_DRIVE_URL = os.getenv("YANDEX_DRIVE_URL")