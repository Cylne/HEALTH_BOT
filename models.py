from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client.healthbot

Reminder = db.reminders
UserSettings = db.usersettings
User = db.users