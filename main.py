import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
from data import db_session

from handlers.commands import *
from handlers.messages import *
from handlers.callbacks import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def main():
    db_session.global_init("db/database.db")

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("gen", generate_image_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("my_images", my_images))
    application.add_handler(CommandHandler("gallery", gallery))

    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^🎨 Создать изображение$'), start_generation))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^🖼 Мои изображения$'), my_images))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex('^🌍 Галерея$'), gallery))
    application.add_handler(MessageHandler(filters.TEXT, get_prompt))

    application.add_handler(CallbackQueryHandler(handle_callback))

    application.run_polling()


if __name__ == '__main__':
    main()
