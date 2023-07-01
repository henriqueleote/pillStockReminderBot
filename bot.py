import config
import json
from telegram.ext import Updater, CommandHandler, CallbackContext
from telegram import Update, Chat, Message
from selenium import webdriver
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
    #context.bot.send_message(chat_id = chat_id, text = 'new pill, TODO')



# Main method
def main():
    print("running")

    # Loads from JSON file
    load_storage()

    # Stop the messaging for every user
    for user_id, pill_user in pill_storage.items():
        pill_user["status"] = "stopped"

    # Saves the JSON file
    save_storage()

    # Initialize the bot
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Register bot command handlers
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('new', newPill))

    # Start the bot
    updater.start_polling()

    # Alert all users the bot is running
    #for chat_id in user_settings.keys():
    #    updater.bot.send_message(chat_id=chat_id, text='The bot has restarted.\nPlease /run to continue getting updates')

    updater.idle()

if __name__ == '__main__':
    main()



















