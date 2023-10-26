import logging

from telegram.ext import CallbackQueryHandler, ConversationHandler
from callbacks_func import callback_func
from main_functions import *
from wish_functions import *
from gia_functions import *
from config import token_tg

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = token_tg


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    text_handler = MessageHandler(Filters.text & ~Filters.command, echo)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("work", subjects))
    dp.add_handler(CommandHandler("profile", profile))
    dp.add_handler(CommandHandler("wish", wish))
    dp.add_handler(CommandHandler("wish10", wish10))
    dp.add_handler(CommandHandler("inventory", show_inventory))
    dp.add_handler(CommandHandler("daily", daily))
    dp.add_handler(CallbackQueryHandler(callback_func))
    dp.add_handler(text_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
