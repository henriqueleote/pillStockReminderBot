# Pill Reminder Bot

This Telegram bot helps you manage your pill reminders. You can add, edit, and delete pills, as well as view the pill information.

## Getting Started

1. Clone the repository: `git clone https://github.com/henriqueleote/pillStockReminderBot.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Create a new Telegram bot and obtain the bot token.
4. Update the `config.py` file with your bot token.

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

