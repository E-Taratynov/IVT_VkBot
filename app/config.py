import os
from dotenv import load_dotenv
from enum import Enum

class DataFiles(Enum):
    SCHEDULE_FILE = 'schedule_file.xlsx'
    GROUPS = 'schedule_by_groups.json'
    CLASSROOMS = 'classrooms.json'
    PROFESSORS = 'professors.json'

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
dotenv_path = os.path.normpath(dotenv_path)
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN = os.getenv("TOKEN")
GOOGLE_DRIVE_URL = os.getenv("GOOGLE_DRIVE_URL")