import re
import time
import uuid
import schedule as schedule
from apscheduler.schedulers.background import BackgroundScheduler

import config
import json
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update, Chat, Message
from datetime import datetime, timedelta, date

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


# Handle the /statusChange command
def statusChange(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if str(chat_id) in pill_storage:
        pill_storage[str(chat_id)]['status'] = 'running' if pill_storage[str(chat_id)]['status'] == 'stopped' else 'stopped'
        context.bot.send_message(chat_id=chat_id, text='Reminders have been updated')
        save_storage()
    else:
        context.bot.send_message(chat_id=chat_id, text='Since you are new, use /help to check the command /new to start')


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

        for chat_id, data in pill_storage.items():
            if "pills" in data:
                for index, pill_data in data["pills"].items():
                    if pill_data['pillName'] == pillName:
                        context.bot.send_message(chat_id=chat_id, text="You can't have duplicate name.")
                        return

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

        context.bot.send_message(chat_id=chat_id, text="Pill added with success")

    else:
        context.bot.send_message(chat_id=chat_id, text="Wrong text syntax. Please use\n/new name, dd-mm-yyyy, perBox, perDay, alertDays\nExample: Pill, 01-01-2000, 10, 3, 2")
        return


# Handle the /edit <text> command
def editPill(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    pillData = update.message.text

    if str(chat_id) not in pill_storage:
        context.bot.send_message(chat_id=chat_id, text="No pills to edit")
        return

    pattern = r'^/edit\s+\w+,\s+[\w\s]+,\s+\d{2}-\d{2}-\d{4},\s+\d+,\s+\d+,\s+\d+$'

    if re.match(pattern, pillData):
        pillToEdit, pillName, startingDate, perBox, perDay, alertDays = map(str.strip, pillData[5:].split(','))

        # Validate pill_date as a valid date
        try:
            datetime.strptime(startingDate, '%d-%m-%Y')
        except ValueError:
            # Invalid date format, send an error message to the user
            context.bot.send_message(chat_id=chat_id, text="Invalid date format. Please use dd-mm-yyyy.")
            return

        # Validate perBox and perDay as numbers
        if not perBox.isdigit() or not perDay.isdigit() or not alertDays.isdigit():
            # Invalid perBox or perDay, send an error message to the user
            context.bot.send_message(chat_id=chat_id, text="Invalid perBox, perDay or alertDays. Please enter only numbers.")
            return

        pillFound = False
        for chat_id, data in pill_storage.items():
            if "pills" in data:
                for index, pill_data in data["pills"].items():
                    if pill_data['pillName'] == pillToEdit:
                        pill_data['pillName'] = pillName
                        pill_data['startingData'] = startingDate
                        pill_data['perBox'] = perBox
                        pill_data['perDay'] = perDay
                        pill_data['alertDays'] = alertDays
                        pillFound = True
                        save_storage()  # Saves the JSON file
                        context.bot.send_message(chat_id=chat_id, text="Pill edited with success")
                        break

        if not pillFound:
            context.bot.send_message(chat_id=chat_id, text="Pill not found for editing")

    else:
        context.bot.send_message(chat_id=chat_id,
                                 text="Wrong text syntax. Please use\n/new name, dd-mm-yyyy, perBox, perDay, alertDays\nExample: Pill, 01-01-2000, 10, 3, 2")
        return

def checkStock(bot):
    print("checking")
    for chat_id, data in pill_storage.items():
        if "status" in data and data["status"] == "running":
            if "pills" in data:
                for index, pill_data in data["pills"].items():
                    if calculateNotificationDate(pill_data)[0]:
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
                                                                   f"Starting date: {pill_data['startingDate']}\n"
                                                                   f"Last pill date: {calculateNotificationDate(pill_data)[1]}\n")


def calculateNotificationDate(pill_data):
    startingDate = datetime.strptime(pill_data['startingDate'], '%d-%m-%Y')
    perDay = int(pill_data['perDay'])
    perBox = int(pill_data['perBox'])
    alertDays = int(pill_data['alertDays'])  # Updated variable name

    # Calculate end date
    last_pill_date = startingDate + timedelta(days=(perDay / perBox) - 1)

    days_until_last = (last_pill_date - datetime.today()).days + 1

    return [days_until_last <= alertDays, last_pill_date.date().strftime('%d-%m-%Y')]


# Main method
def main():
    print("running")

    load_storage()  # Loads from JSON file

    save_storage()  # Saves the JSON file

    # Initialize the bot
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Register bot command handlers
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('new', newPill))
    dispatcher.add_handler(CommandHandler('all', showAll))
    dispatcher.add_handler(CommandHandler('start', statusChange))
    dispatcher.add_handler(CommandHandler('stop', statusChange))
    dispatcher.add_handler(CommandHandler('edit', editPill))
    dispatcher.add_handler(CommandHandler('delete', statusChange))

    schedule.every().day.at("13:00").do(lambda: checkStock(updater.bot))
    updater.start_polling()  # Start the bot

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()







