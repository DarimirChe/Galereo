import time
from datetime import datetime

from image_generator import ImageGenerator
import config
import logging
from telegram.ext import Application, CommandHandler
from config import BOT_TOKEN
from data import db_session
from data.users import User
from data.images import Image

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def generate_image(update, context):
    prompt = " ".join(context.args)
    pipeline_id = generator.get_pipeline()
    uuid = generator.generate(prompt, pipeline_id)

    delay = 5
    sent_message = await update.message.reply_text(f"Изображение генерируется.")
    for i in range(10, 0, -1):
        images = generator.check_generation(uuid)
        if images is not None:
            break
        await sent_message.edit_text(f"Изображение генерируется. Осталось примерно {i * delay} с.")
        time.sleep(delay)

    await sent_message.edit_text("Изображение отправляется...")

    user = update.effective_user
    telegram_id = user.id
    path = f"data/images/image_{telegram_id}_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.jpg"
    image_bytes = generator.save_image(images, path)

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_bytes,
                                 caption=f"Изображение по запросу: {prompt}")
    await sent_message.delete()

    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()
    if user is None:
        user = User()
        user.telegram_id = telegram_id
        db_sess.add(user)
        db_sess.commit()

    image = Image()
    image.path = path
    image.prompt = prompt
    image.user_id = user.id
    db_sess.add(image)
    db_sess.commit()
    db_sess.close()


async def help_command(update, context):
    await update.message.reply_text("/gen <запрос> -- генерация изображения по запросу.")


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я Galereo-бот, могу создавать изображения по запросу. Введите /help чтобы увидеть список команд.",
    )

    telegram_id = user.id

    db_sess = db_session.create_session()
    existing_user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()

    if not existing_user:
        user = User()
        user.telegram_id = telegram_id
        db_sess.add(user)
        db_sess.commit()
    db_sess.close()


def main():
    db_session.global_init("db/database.db")

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("gen", generate_image))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", start))
    application.run_polling()


if __name__ == '__main__':
    generator = ImageGenerator("https://api-key.fusionbrain.ai/", config.API_KEY, config.SECRET_KEY)
    main()
