import os
from dotenv import load_dotenv
from enum import Enum

class DataFiles(Enum):
    SCHEDULE_FILE = 'schedule_file.xlsx'
    USERS_FILE = 'users.json'
    STUDENTS_FILE = 'students.json'
    GROUPS = 'schedule_by_groups.json'
    CLASSROOMS = 'classrooms.json'
    PROFESSORS = 'professors.json'

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
dotenv_path = os.path.normpath(dotenv_path)
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

API_URL = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?'
TOKEN = os.getenv("TOKEN")
GOOGLE_DRIVE_URL = os.getenv("GOOGLE_DRIVE_URL")
YANDEX_DRIVE_URL = os.getenv("YANDEX_DRIVE_URL")