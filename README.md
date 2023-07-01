# Pill Reminder Bot

Pill Reminder Bot is a Telegram bot that helps you manage your medication schedule and sends reminders for pill refills. With this bot, you can easily set up pill reminders, track your medication intake, and receive notifications when it's time to restock your pills.

## Getting Started

1. Clone the repository: `git clone https://github.com/henriqueleote/pillStockReminderBot.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Create a new Telegram bot and obtain the bot token.
4. Update the `config.py` file with your bot token.

## Features

- Create new pill entries with customizable details such as pill name, starting date, pills per box, pills per day, and alert days.
- Edit existing pill entries to update information such as pill name, starting date, pills per box, pills per day, and alert days.
- Delete unwanted pill entries from your list.
- Check the status of your pill reminders.
- Get notifications when it's time to restock your pills based on the configured alert days.
- View all your pill entries with their respective details.

## Usage

The bot supports the following commands:

- `/help` - Display the available commands and their usage.
- `/new <pill_data>` - Add a new pill. The `<pill_data>` should be in the format: `<pill_name>, <starting_date>, <pills_per_box>, <pills_per_day>, <alert_days>`. For example: `/new Pill A, 01-01-2023, 10, 2, 3`.
- `/all` - Display all the pills and their details.
- `/start` - Start receiving pill reminders.
- `/stop` - Stop receiving pill reminders.
- `/edit <pill_data>` - Edit an existing pill. The `<pill_data>` should be in the format: `<old_name>, <new_name>, <starting_date>, <pills_per_box>, <pills_per_day>, <alert_days>`. For example: `/edit Pill A, Pill B, 10-02-2023, 20, 3, 5`.
- `/delete <pill_name>` - Delete a pill by its name. For example: `/delete Pill A`.

## Example

Here's an example of how you can interact with the bot:

1. Add a new pill: `/new Pill A, 01-01-2023, 10, 2, 3`
2. View all pills: `/all`
3. Start receiving reminders: `/start`
4. Edit a pill: `/edit Pill A, Pill B, 10-02-2023, 20, 3, 5`
5. Delete a pill: `/delete Pill B`

## License

This project is licensed under the MIT License. See the LICENSE file for more information.
