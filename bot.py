import re
import uuid
import schedule as schedule

import config
import json
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update, Chat, Message
from datetime import datetime, timedelta

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


# Handle the /new <text> command
def newPill(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    pillData = update.message.text
    if str(chat_id) not in pill_storage:
        pill_storage[str(chat_id)] = {
            'pills': {},
            'status': "running"
        }
        save_storage()

    pattern = r'^/new\s+[\w\s]+,\s+\d{2}-\d{2}-\d{4},\s+\d+,\s+\d+,\s+\d+$'


    if re.match(pattern, pillData):
        pillName, startingDate, perBox, perDay, alertDays = map(str.strip, pillData[4:].split(','))

        # Validate pill_date as a valid date
        try:
            datetime.strptime(startingDate, '%d-%m-%Y')
        except ValueError:
            # Invalid date format, send an error message to the user
            context.bot.send_message(chat_id=chat_id,text="Invalid date format. Please use dd-mm-yyyy.")
            return

        # Validate perBox and perDay as numbers
        if not perBox.isdigit() or not perDay.isdigit() or not alertDays.isdigit():
            # Invalid perBox or perDay, send an error message to the user
            context.bot.send_message(chat_id=chat_id, text="Invalid perBox, perDay or alertDays. Please enter only numbers.")
            return
    else:
        context.bot.send_message(chat_id=chat_id, text="Wrong text syntax. Please use\n/new name, dd-mm-yyyy, perBox, perDay, alertDays\nExample: Pill, 01-01-2000, 10, 3, 2")
        return

    addPill(context, chat_id, pillName, startingDate, perBox, perDay, alertDays)


def addPill(context, chat_id, pillName, startingDate, perBox, perDay, alertDays):

    pillID = str(uuid.uuid4())  # Generate a pillID using a unique identifier like UUID

    # Create the pill entry using the pillID as the key
    pill_storage[str(chat_id)]['pills'][pillID] = {
        'pillName': pillName,
        'startingDate': startingDate,
        'perBox': perBox,
        'perDay': perDay,
        'alertDays': alertDays
    }

    save_storage()  # Saves the JSON file

    context.bot.send_message(chat_id=chat_id,text="Pill added with success")

def checkStock(bot):
    for chat_id, data in pill_storage.items():
        if "status" in data and data["status"] == "running":
            if "pills" in data:
                for index, pill_data in data["pills"].items():
                    if datetime.now().date() == calculateNotificationDate(pill_data):
                        bot.send_message(chat_id=chat_id, text=f"You need to restock {pill_data['pillName']}, stock ends in {pill_data['alertDays']} days")


# Handle the /help command
def showAll(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if str(chat_id) in pill_storage:
        for chat_id, data in pill_storage.items():
            if "pills" in data:
                for index, pill_data in data["pills"].items():
                    context.bot.send_message(chat_id=chat_id, text=f""
                                                                   f"Name: {pill_data['pillName']}\n"
                                                                   f"Pill per day: {pill_data['perDay']}\n"
                                                                   f"Pills per box: {pill_data['perBox']}\n"
                                                                   f"Last pill date: {(calculateNotificationDate(pill_data) + timedelta(days=int(pill_data['alertDays'])))}\n")


def calculateNotificationDate(pill_data):
    startingDate = datetime.strptime(pill_data['startingDate'], '%d-%m-%Y')
    perDay = int(pill_data['perDay'])
    perBox = int(pill_data['perBox'])
    alertDays = int(pill_data['alertDays'])  # Updated variable name

    # Calculate end date
    last_pill_date = startingDate + timedelta(days=(perDay / perBox) - 1)

    # Calculate notification date
    notification_date = last_pill_date - timedelta(days=alertDays)

    print(notification_date)

    return notification_date.date()

# Main method
def main():
    print("running")

    load_storage()  # Loads from JSON file

    #Stop the messaging for every user
    #for user_id, pill_user in pill_storage.items():
    #    pill_user["status"] = "stopped"


    save_storage()  # Saves the JSON file


    # Initialize the bot
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Register bot command handlers
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('new', newPill))
    dispatcher.add_handler(CommandHandler('all', showAll))

    #while True:
        #schedule.every().day.at("12:00").do(lambda: checkStock(updater.bot))

    checkStock(updater.bot)

    updater.start_polling() # Start the bot

    # Alert all users the bot is running
    #for chat_id in user_settings.keys():
    #    updater.bot.send_message(chat_id=chat_id, text='The bot has restarted.\nPlease /run to continue getting updates')

    updater.idle()

if __name__ == '__main__':
    main()



















