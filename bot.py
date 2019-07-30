import logging
import os
import sys

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler
from telegram.ext.filters import Filters
from statements import Statements

# Enabling logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

sttmnts = Statements()

# Getting mode, so we could define run function for local and Heroku setup
mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")

if mode == "dev":
    def run(updater):
        updater.start_polling()
elif mode == "prod":
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        # Code from https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks#heroku
        updater.start_webhook(listen="0.0.0.0",
                              port=PORT,
                              url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
else:
    logger.error("No MODE specified!")
    sys.exit(1)


STATE = range(1)

def record_message(message, parent = None):
    chat_id = message.chat.id
    message_id = message.message_id
    user_id = message.from_user.id
    text = message.text
    sttmnts.add(chat_id, message_id, user_id, text, parent)


def start_handler(bot, update):
    # Creating a handler-function for /start command
    user = update.message.from_user
    user_name = user.first_name + " " + user.last_name
    logger.info("User {} started bot".format(user_name))
    update.message.reply_text("{} please make your statement:".format(user_name))
    return STATE


def state_handler(bot, update):
    # Creating a handler-function for /state command
    logger.info("User responded with a statement")
    record_message(update.message, None)
    update.message.reply_text('I hear you')
    return ConversationHandler.END


def cancel_handler(bot, update):
    update.message.reply_text("statement recording was canceled")
    return ConversationHandler.END


def reply_handler(bot, update):
    logger.info('caught a reply')
    orig = update.message.reply_to_message
    if(sttmnts.get(orig.chat.id, orig.message_id) != None and
        orig.chat.id == update.message.chat.id):
        record_message(update.message, orig.message_id)
        update.message.reply_text('I hear you')


if __name__ == '__main__':
    logger.info("Starting bot")
    updater = Updater(TOKEN)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_handler)],
        states={
            STATE: [MessageHandler(Filters.text, state_handler),
                    CommandHandler('cancel', cancel_handler)],
        },
        fallbacks=[MessageHandler(Filters.all, cancel_handler)]
    )
    updater.dispatcher.add_handler(conv_handler)

    updater.dispatcher.add_handler(MessageHandler(Filters.reply, reply_handler))

    run(updater)
