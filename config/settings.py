import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(f'{BASE_DIR}/.env')

BOT_TOKEN = os.getenv('BOT_TOKEN')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
DBNAME = os.getenv('DBNAME')
USER = os.getenv('USER')
PASSWORD = os.getenv('PASSWORD')

CHANNEL_ID = int(os.getenv('CHANNEL_ID', '0'))
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')

ADMIN_IDS = [
    int(admin_id.strip())
    for admin_id in os.getenv('ADMIN_IDS', '').split(',')
    if admin_id.strip().isdigit()
]