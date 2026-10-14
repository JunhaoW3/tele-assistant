import re
from random import randint
import logging
import os

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


load_dotenv()

# The API Key we received for our bot
TELEGRAM_API_KEY = os.getenv('TELEGRAM_API_KEY')
if not TELEGRAM_API_KEY:
    raise RuntimeError("TELEGRAM_API_KEY is missing from the environment or .env file")

# Our states, as integers
WELCOME = 0
QUESTION = 1
CANCEL = 2
CORRECT = 3

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # send the question, and show the keyboard markup (suggested answers)
    await update.message.reply_text(
        "Hello there, do you want to answer a question? (Yes/No)",
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], one_time_keyboard=True),
    )
    return WELCOME

# Helper function to generate new numbers and send the questions
async def randomise_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # store the numbers in the context
    context.user_data['rand_x'], context.user_data['rand_y'] = randint(0, 1000), randint(0, 1000)
    # send the question
    await update.message.reply_text(
        f"Calculate {context.user_data['rand_x']}+{context.user_data['rand_y']}"
    )

# In WELCOME state, check if the user wants to answer a question
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.lower() in ['yes', 'y']:
        # send question, and go to QUESTION state
        await randomise_numbers(update, context)
        return QUESTION
    else:
        return CANCEL

# In QUESTION state
async def question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # expected solution
    solution = int(context.user_data['rand_x']) + int(context.user_data['rand_y'])
    # Check if solution is correct
    if solution == int(update.message.text):
        await update.message.reply_text("Correct answer!")
        await update.message.reply_text("Was this tutorial helpful to you?")
        return CORRECT
    else:
        await update.message.reply_text("Wrong answer")
        await randomise_numbers(update, context)
        return QUESTION

async def correct(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.lower() in ['yes', 'y']:
        await update.message.reply_text("Glad it was useful!")
    else:
        await update.message.reply_text("You must be a programming wizard already!")
    # get the user's first name
    first_name = update.effective_user.first_name
    await update.message.reply_text(f"See you {first_name}!, bye")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # get the user's first name
    first_name = update.effective_user.first_name
    await update.message.reply_text(
        f"Okay, no question for you then, take care, {first_name}!",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

# a regular expression that matches yes or no
yes_no_regex = re.compile(r'^(yes|no|y|n)$', re.IGNORECASE)
# Create our ConversationHandler, with only one state
handler = ConversationHandler(
      entry_points=[CommandHandler('start', start)],
      states={
            WELCOME: [MessageHandler(filters.Regex(yes_no_regex), welcome)],
            QUESTION: [MessageHandler(filters.Regex(r'^\d+$'), question)],
            CANCEL: [MessageHandler(filters.Regex(yes_no_regex), cancel)],
            CORRECT: [MessageHandler(filters.Regex(yes_no_regex), correct)],
      },
      fallbacks=[CommandHandler('cancel', cancel)],
      )

def main() -> None:
    application = Application.builder().token(TELEGRAM_API_KEY).build()
    application.add_handler(handler)
    application.run_polling()


if __name__ == '__main__':
    main()
