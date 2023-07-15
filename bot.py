import re
import time
import uuid
import schedule as schedule

import config
import json
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update, Chat, Message
from datetime import datetime, timedelta, date

# Telegram bot token
bot_token = config.bot_token

# Global variables
pill_storage = {}
TIME = "13:00"
ALERT_EMOJI = "\u26A0"  # Unicode for the warning sign emoji
CHECKMARK_EMOJI = "\u2705"  # Unicode for the green checkmark emoji
WRONG_EMOJI = "\u274C"  # Unicode for the cross mark emoji

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
    context.bot.send_message(chat_id = chat_id, text = f"Welcome to the Pill Reminder, this is a Telegram bot coded by Henrique Leote in Python that alerts you on near stock shortage of pills, so that you never run out of.\n\n"
                                                       f"/help: Shows this menu\n"
                                                       f"/new <pill_data>: Adds a new pill.\n"
                                                       f"/all: Display all the pills and their details.\n"
                                                       f"/start: Start receiving pill reminders (is on by default).\n"
                                                       f"/stop - Stop receiving pill reminders.\n"
                                                       f"/edit <pill_data>: Edits an existing pill.\n"
                                                       f"/delete <pill_name>: Delete a pill by its name.\n"
                                                       f"The stock is checked every day at {TIME} - Austrian Time.\n"
                                                       f"If the bot doesn't respond to a command, it's because it's offline at the moment.")


# Handle the /statusChange command
def statusChange(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if str(chat_id) in pill_storage:
        pill_storage[str(chat_id)]['status'] = 'running' if pill_storage[str(chat_id)]['status'] == 'stopped' else 'stopped'
        context.bot.send_message(chat_id=chat_id, text='Reminders have been updated.')
        save_storage()
    else:
        context.bot.send_message(chat_id=chat_id, text='Since you are new, use /help to start.')


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
            context.bot.send_message(chat_id=chat_id,text=f"{WRONG_EMOJI} Invalid date format. Please use dd-mm-yyyy. {WRONG_EMOJI}")
            return

        # Validate perBox and perDay as numbers
        if not perBox.isdigit() or not perDay.isdigit() or not alertDays.isdigit():
            # Invalid perBox or perDay, send an error message to the user
            context.bot.send_message(chat_id=chat_id, text=f"{WRONG_EMOJI} Invalid perBox, perDay or alertDays. Please enter only numbers. {WRONG_EMOJI}")
            return

        if str(chat_id) in pill_storage:
            data = pill_storage[str(chat_id)]
            if "pills" in data:
                for index, pill_data in data["pills"].items():
                    if pill_data['pillName'] == pillName:
                        context.bot.send_message(chat_id=chat_id, text=f"{WRONG_EMOJI} You can't have a duplicate pill name. {WRONG_EMOJI}")
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
        pill_storage[str(chat_id)]['status'] = "running"

        save_storage()  # Saves the JSON file

        context.bot.send_message(chat_id=chat_id, text=f"{CHECKMARK_EMOJI} Pill added with success. {CHECKMARK_EMOJI}")

    else:
        context.bot.send_message(chat_id=chat_id, text="Please use:\n"
                                                       "/new name, dd-mm-yyyy, perBox, perDay, alertDays\n"
                                                       "perBox: Number of pills per box\n"
                                                       "perDay: Number of pills you take per day\n"
                                                       "alertDays: Number of days in advance to be alerted to restock\n"
                                                       "Example: /new Pill, 01-01-2000, 10, 3, 2")
        return


# Handle the /edit <text> command
def editPill(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    pillData = update.message.text

    if str(chat_id) not in pill_storage:
        context.bot.send_message(chat_id=chat_id, text=f"{WRONG_EMOJI} No pills to edit. {WRONG_EMOJI}")
        return

    pattern = r'^/edit\s+\w+,\s+[\w\s]+,\s+\d{2}-\d{2}-\d{4},\s+\d+,\s+\d+,\s+\d+$'

    if re.match(pattern, pillData):
        pillToEdit, pillName, startingDate, perBox, perDay, alertDays = map(str.strip, pillData[5:].split(','))

        # Validate pill_date as a valid date
        try:
            datetime.strptime(startingDate, '%d-%m-%Y')
        except ValueError:
            # Invalid date format, send an error message to the user
            context.bot.send_message(chat_id=chat_id, text=f"{WRONG_EMOJI} Invalid date format. Please use dd-mm-yyyy. {WRONG_EMOJI}")
            return

        # Validate perBox and perDay as numbers
        if not perBox.isdigit() or not perDay.isdigit() or not alertDays.isdigit():
            # Invalid perBox or perDay, send an error message to the user
            context.bot.send_message(chat_id=chat_id, text=f"{WRONG_EMOJI} Invalid perBox, perDay or alertDays. Please enter only numbers. {WRONG_EMOJI}")
            return

        pillFound = False
        goodToEdit = False

        if(pillName == pillToEdit):
            goodToEdit = True
        else:
            if str(chat_id) in pill_storage:
                data = pill_storage[str(chat_id)]
                if "pills" in data:
                    pills_data = data["pills"]
                    for pill_id, pill_data in pills_data.items():
                        if pill_data['pillName'] == pillName:
                            goodToEdit = False
                            context.bot.send_message(chat_id=chat_id,
                                                     text=f"{WRONG_EMOJI} You can't have a duplicate pill name. {WRONG_EMOJI}")
                            return

        if goodToEdit:
            if str(chat_id) in pill_storage:
                data = pill_storage[str(chat_id)]
                if "pills" in data:
                    pills_data = data["pills"]
                    for pill_id, pill_data in pills_data.items():
                        if pill_data['pillName'] == pillToEdit:
                            id = pill_id
            # Update the pill data
            pill_data = {
                'pillName': pillName,
                'startingDate': startingDate,
                'perBox': perBox,
                'perDay': perDay,
                'alertDays': alertDays
            }
            pills_data[id] = pill_data
            save_storage()  # Saves the JSON file
            context.bot.send_message(chat_id=chat_id,
                                     text=f"{CHECKMARK_EMOJI} Pill edited successfully. {CHECKMARK_EMOJI}")
            pillFound = True


        if not pillFound:
            context.bot.send_message(chat_id=chat_id, text=f"{WRONG_EMOJI} Pill not found to edit. {WRONG_EMOJI}")
            return

    else:
        context.bot.send_message(chat_id=chat_id,
                                 text="Please use:\n"
                                      "/edit oldName, newName, dd-mm-yyyy, perBox, perDay, alertDays\n"
                                      "perBox: Number of pills per box\n"
                                      "perDay: Number of pills you take per day\n"
                                      "alertDays: Number of days in advance to be alerted to restock\n"
                                      "Example: /edit Old, New, 25-12-2024, 12, 5, 3\n"
                                      "Everything can be changed, but the name of the existing must be correct.")
        return


# Handle the /delete <text> command
def deletePill(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    pillDeleted = False

    if str(chat_id) not in pill_storage:
        context.bot.send_message(chat_id=chat_id, text=f"{WRONG_EMOJI} No pills to delete. {WRONG_EMOJI}")
        return

    pillName = context.args[0]
    if pillName.strip():
        if str(chat_id) in pill_storage:
            data = pill_storage[str(chat_id)]
            if "pills" in data:
                pills_data = data["pills"]
                for pill_id, pill_data in pills_data.items():
                    if pill_data['pillName'] == pillName:
                        del data["pills"][pill_id]
                        pillDeleted = True
                        save_storage()  # Saves the JSON file
                        context.bot.send_message(chat_id=chat_id, text=f"{CHECKMARK_EMOJI} Pill deleted with success. {CHECKMARK_EMOJI}")
                        break

        if not pillDeleted:
            context.bot.send_message(chat_id=chat_id, text=f"{WRONG_EMOJI} Pill not found to delete. {WRONG_EMOJI}")
            return

    else:
        context.bot.send_message(chat_id=chat_id, text="Please use:\n"
                                                       "/delete name\n"
                                                       "Example: /delete mypill")
        return


def checkStock(bot):
    print("checking")
    for chat_id, data in pill_storage.items():
        if "status" in data and data["status"] == "running":
            if "pills" in data:
                for index, pill_data in data["pills"].items():
                    if calculateNotificationDate(pill_data)[0]:
                        bot.send_message(chat_id=chat_id, text=f"{ALERT_EMOJI} You need to restock {pill_data['pillName']}, stock ends in {calculateNotificationDate(pill_data)[2]} days. {ALERT_EMOJI}")


# Handle the /help command
def showAll(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    pillShown = False
    if str(chat_id) in pill_storage:
        data = pill_storage[str(chat_id)]
        if "pills" in data:
            for index, pill_data in data["pills"].items():
                pillShown = True
                context.bot.send_message(chat_id=chat_id, text=f""
                                                               f"Name: {pill_data['pillName']}\n"
                                                               f"Pill per day: {pill_data['perDay']}\n"
                                                               f"Pills per box: {pill_data['perBox']}\n"
                                                               f"Starting date: {pill_data['startingDate']}\n"
                                                               f"Last pill date: {calculateNotificationDate(pill_data)[1]}\n")

    if not pillShown:
        context.bot.send_message(chat_id=chat_id,
                         text=f"{WRONG_EMOJI} No pills to show. {WRONG_EMOJI}")
        return

def calculateNotificationDate(pill_data):
    startingDate = datetime.strptime(pill_data['startingDate'], '%d-%m-%Y')
    perDay = int(pill_data['perDay'])
    perBox = int(pill_data['perBox'])
    alertDays = int(pill_data['alertDays'])  # Updated variable name

    # Calculate end date
    last_pill_date = startingDate + timedelta(days=(perDay / perBox) - 1)

    days_until_last = (last_pill_date - datetime.today()).days + 1

    if days_until_last <= 0:
        days_until_last = 0

    return [days_until_last <= alertDays, last_pill_date.date().strftime('%d-%m-%Y'), days_until_last]


# Main method
def main():
    print("running")

    load_storage()  # Loads from JSON file

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
    dispatcher.add_handler(CommandHandler('delete', deletePill))

    schedule.every().day.at(TIME).do(lambda: checkStock(updater.bot))
    updater.start_polling()  # Start the bot
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()







