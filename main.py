import re
from random import randint
import logging
import os
from openai import OpenAI

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
AI_API_KEY = os.getenv('AI_API_KEY')

def start(update, context):
    context.reply_text("Hello! I'm Wigglethorpe. Ask me anything!")

def handle_message(update, context):
    user_input = update.message.text
    client = OpenAI(api_key=AI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": user_input}]
    )
    context.reply_text(response.choices[0].message["content"])

if __name__ == '__main__':
    app = Application.builder().token(TELEGRAM_API_KEY).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
