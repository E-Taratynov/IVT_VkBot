import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
dotenv_path = os.path.normpath(dotenv_path)
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

TOKEN = os.getenv("TOKEN")
GOOGLE_DRIVE_URL = os.getenv("GOOGLE_DRIVE_URL")