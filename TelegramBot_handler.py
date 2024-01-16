"""
CodeBuddy, is designed to challenge users with coding tasks.
It uses OpenAI's API to generate and evaluate tasks based on difficulty levels.

TelegramBot_handler - main file, used to work with Telegram bot.
Update all import API tokens in configuration/config.yml
"""

# Imports to work with Telegram and OpenAI

from telegram import *
from telegram.ext import *
import yaml
from OpenAI_receiver import call_task, call_check_task


# Loading the YAML file with all information

with open('configuration/config.yml', 'r') as file:
    config = yaml.safe_load(file)
user_tasks = {}
awaiting_solution = {}

def escape_markdown(text: str) -> str:
    """
    Escapes markdown function adapts the given text to MarkdownV2 format.
    """
    escape_chars = '_[]()~`>#+-=|{}.!'
    return ''.join('\\' + char if char in escape_chars else char for char in text)

start_message = escape_markdown(config['prompts']['start_message'])
task_selection_message = escape_markdown(config['prompts']['task_selection_message'])
help_message = escape_markdown(config['prompts']['help_message'])

def build_menu(buttons: list, n_cols: int, header_buttons=None, footer_buttons=None) -> list:
    """
    Function for building the menu buttons under the the message
    """
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

async def task_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Function to handle `/task` command
    """
    list_of_diff = ['Easy Peasy', 'Medium Madness', 'Hardcore Hacker']
    button_list = []
    for each in list_of_diff:
        button_list.append(InlineKeyboardButton(each, callback_data=each))
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    await update.message.reply_text(task_selection_message, parse_mode='MarkdownV2', reply_markup=reply_markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Function to handle `/start` command
    """
    await update.message.reply_text(start_message, parse_mode="MarkdownV2")

async def help_sender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Function to handle `/help` command
    """
    await update.message.reply_text(help_message, parse_mode="MarkdownV2")

async def handle_message(update: Update, context: CallbackContext) -> None:
    """
    Function to receive solved code from the user, send to OpenAI_receiver and get a feedback
    """
    user_id = update.effective_user.id
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Yes", callback_data="submit_solution_again"),
        InlineKeyboardButton("No", callback_data="no_submit_again")]
    ])
    
    if awaiting_solution.get(user_id):
        solution = update.message.text
        task_definition = user_tasks.get(user_id)

        if task_definition:
            response = call_check_task(solution, task_definition)
            
            await context.bot.send_message(chat_id=user_id, text=response)
            await context.bot.send_message(chat_id=user_id, text="Would you like to submit again?", reply_markup = reply_markup)
        else:
            await context.bot.send_message(chat_id=user_id, text="Oops! I couldn't find your task. Let's start over, use /task to select a new task.")

async def handle_task_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Function for giving a list of dificulties of tasks and calling the function with OpenAI task creation
    """
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    
    user_choice = query.data  # Options: 'Easy Peasy', 'Medium Madness', 'Hardcore Hacker' or 'Submit solution'
    
    if user_choice in ['Easy Peasy', 'Medium Madness', 'Hardcore Hacker']:
        task_difficulty = {'Easy Peasy': 0, 'Medium Madness': 1, 'Hardcore Hacker': 2}[user_choice]
        await query.edit_message_text(text=f"You selected: {user_choice}. \nWait a second, the bot is creating a task for you!")
        task_definition = call_task(task_difficulty)
        user_tasks[user_id] = task_definition
        
        button = InlineKeyboardButton("Submit solution", callback_data="submit_solution")
        reply_markup = InlineKeyboardMarkup([[button]])
        await context.bot.send_message(chat_id=user_id, text=task_definition, reply_markup=reply_markup)
    
    elif user_choice == 'submit_solution':
        awaiting_solution[user_id] = True
        await context.bot.send_message(chat_id=user_id, text="To submit your solution, just send the code as a message. Do not send a file. Waiting for your response!")
    
    elif user_choice == 'submit_solution_again':

        awaiting_solution[user_id] = True
        await context.bot.send_message(chat_id=user_id, text="Please, send your new solution.")

    elif user_choice == 'no_submit_again':

        await context.bot.send_message(chat_id=user_id, text="Thank you for this task! Press /start or /task to continue")
        if user_id in user_tasks:
            del user_tasks[user_id]
            del awaiting_solution[user_id]

    
# Telegram app configuration.

app = ApplicationBuilder().token(config['setup'][1]['TelegramBOT_API']).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("task", task_selection))
app.add_handler(CommandHandler("help", help_sender))
app.add_handler(CallbackQueryHandler(handle_task_selection))
app.add_handler(MessageHandler(None, handle_message))

app.run_polling()
