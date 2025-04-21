import time
from image_generator import ImageGenerator
import config
import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler
from config import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def generate_image(update, context):
    prompt = " ".join(context.args)
    await update.message.reply_text(prompt)
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

    await sent_message.delete()
    image_bytes = generator.save_image(images)
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_bytes,
                                 caption=f"Изображение по запросу: {prompt}")


async def help_command(update, context):
    await update.message.reply_text("/gen <запрос> -- генерация изображения по запросу.")


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я Galereo-бот, могу создавать изображения по запросу. Введите /help чтобы увидеть список команд.",
    )


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    # text_handler = MessageHandler(filters.TEXT, generate_image)
    # application.add_handler(text_handler)
    application.add_handler(CommandHandler("gen", generate_image))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start", start))
    application.run_polling()


if __name__ == '__main__':
    generator = ImageGenerator("https://api-key.fusionbrain.ai/", config.API_KEY, config.SECRET_KEY)
    main()
