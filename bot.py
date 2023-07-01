import config
import json
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update, Chat, Message
from selenium import webdriver
from datetime import datetime
import os, psutil

# Telegram bot token
bot_token = config.bot_token;

# Global variables
pill_storage = {}

# Local storage files
STORAGE_FILE = 'pill_storage.json'

# Load storage from the JSON file
def load_storage():
    global pill_storage
    try:
        with open(STORAGE_FILE, 'r') as file:
            data = file.read()
            if data:
                pill_storage = json.loads(data)
            else:
                pill_storage = {}
    except FileNotFoundError:
        pill_storage = {}


# Save storage to the JSON file
def save_storage():
    with open(STORAGE_FILE, 'w') as file:
        if pill_storage:
            json.dump(pill_storage, file)
        else:
            file.write('')