from pymongo import MongoClient
from config import MONGO_URI, SECRET_KEY

client = MongoClient(MONGO_URI)
db = client["dietplannerDB"]
users = db.users
