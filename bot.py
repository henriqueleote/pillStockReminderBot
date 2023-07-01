import re
import uuid

import config
import json
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update, Chat, Message
from datetime import datetime

# Telegram bot token
bot_token = config.bot_token

# Global variables
pill_storage = {}

# Local storage files
STORAGE_FILE = 'pill_storage.json'

# STORAGE METHODS

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



# TELEGRAM Command handlers

# Handle the /help command
def help(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(chat_id = chat_id, text = 'HELP, TODO')


# Handle the /help command
def newPill(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    pillData = update.message.text
    if str(chat_id) not in pill_storage:
        pill_storage[str(chat_id)] = {
            'pills': {},
            'status': "running"
        }
        #context.bot.send_message(chat_id=chat_id, text='Welcome')
        save_storage()

    pattern = r'^/new\s+[\w\s]+,\s+\d{2}-\d{2}-\d{4},\s+\d+,\s+\d+$'


    if re.match(pattern, pillData):
        pill_name, pill_date, perBox, perDay = map(str.strip, pillData[5:].split(','))

        # Validate pill_date as a valid date
        try:
            datetime.strptime(pill_date, '%d-%m-%Y')
        except ValueError:
            # Invalid date format, send an error message to the user
            context.bot.send_message(chat_id=chat_id,text="Invalid date format. Please use dd-mm-yyyy.")
            return

        # Validate perBox and perDay as numbers
        if not perBox.isdigit() or not perDay.isdigit():
            # Invalid perBox or perDay, send an error message to the user
            context.bot.send_message(chat_id=chat_id, text="Invalid perBox or perDay. Please enter numbers.")
            return
    else:
        context.bot.send_message(chat_id=chat_id, text="Wrong text syntax. Please use\n/new name, dd-mm-yyyy, number, number\nExample: Pill, 01-01-2000, 10, 3")
        return

    addPill(context, chat_id, pill_name, pill_date, perBox, perDay)


def addPill(context, chat_id, pill_name, pill_date, perBox, perDay):

    pillID = str(uuid.uuid4())  # Generate a pillID using a unique identifier like UUID

    # Create the pill entry using the pillID as the key
    pill_storage[str(chat_id)]['pills'][pillID] = {
        'pill_name': pill_name,
        'pill_date': pill_date,
        'perBox': perBox,
        'perDay': perDay
    }

    save_storage()  # Saves the JSON file

    context.bot.send_message(chat_id=chat_id,text="Pill created with success")


# Main method
def main():
    print("running")

    load_storage()  # Loads from JSON file

    # Stop the messaging for every user
    #for user_id, pill_user in pill_storage.items():
    #    pill_user["status"] = "stopped"


    save_storage()  # Saves the JSON file


    # Initialize the bot
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Register bot command handlers
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('new', newPill))

    updater.start_polling() # Start the bot

    # Alert all users the bot is running
    #for chat_id in user_settings.keys():
    #    updater.bot.send_message(chat_id=chat_id, text='The bot has restarted.\nPlease /run to continue getting updates')

    updater.idle()

if __name__ == '__main__':
    main()



















