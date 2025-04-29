import time
from datetime import datetime
import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

from image_generator import ImageGenerator
import config
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from config import BOT_TOKEN
from data import db_session
from data.users import User
from data.images import Image
from keyboards import main_menu_keyboard, get_my_image_keyboard

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


# Запуск генерации через кнопку "Создать изображение"
async def start_generation(update, context):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data="cancel_write_prompt")]])
    await update.message.reply_text("Введите запрос", reply_markup=keyboard)
    context.user_data['waiting_for_prompt'] = True


# Запуск генерации изображения через команду
async def generate_image_command(update, context):
    context.user_data['waiting_for_prompt'] = False
    if context.args:
        prompt = " ".join(context.args)
        await generate_image(prompt, update, context)
    else:
        await update.message.reply_text("Запрос не может быть пустым.")


# Получить запрос из сообщения если пользователь выбрал "Создать изображение"
async def get_prompt(update, context):
    if context.user_data.get('waiting_for_prompt'):
        prompt = update.message.text
        context.user_data['waiting_for_prompt'] = False
        await generate_image(prompt, update, context)
    else:
        await update.message.reply_text("Я вас не понял. Используйте меню или команды.")


# Сама генерация изображения
async def generate_image(prompt, update, context):
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
        reply_markup=main_menu_keyboard
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


async def my_images(update, context):
    user = update.effective_user
    context.user_data['waiting_for_prompt'] = False
    telegram_id = user.id
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()
    images = db_sess.query(Image).filter(Image.user_id == user.id).all()
    db_sess.close()
    if len(images) == 0:
        await update.message.reply_text("У вас нету изображений")
        return
    context.user_data['images'] = images
    context.user_data['current_index'] = 0

    with open(images[0].path, mode="rb") as im:
        image_bytes = im.read()
    my_image_keyboard = get_my_image_keyboard(images[0].like_count, images[0].dislike_count, images[0].is_public)
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=image_bytes,
        caption=images[0].prompt, reply_markup=my_image_keyboard
    )


async def gallery(update, context):
    context.user_data['waiting_for_prompt'] = False
    await update.message.reply_text("Посмотреть галерею")


async def edit_my_images_message(context, query):
    images = context.user_data["images"]
    index = context.user_data["current_index"]
    image = images[index]

    with open(image.path, "rb") as f:
        image_bytes = f.read()

    await query.message.edit_media(
        media=InputMediaPhoto(
            media=image_bytes,
            caption=image.prompt
        ),
        reply_markup=get_my_image_keyboard(image.like_count, image.dislike_count, image.is_public)
    )


# Обработчик нажатий inline кнопок
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_write_prompt":
        context.user_data['waiting_for_prompt'] = False
        await query.message.delete()

    if query.data == "next":
        context.user_data["current_index"] += 1
        index = context.user_data["current_index"]
        images = context.user_data["images"]
        if index >= len(images):
            index = 0
        context.user_data["current_index"] = index
        await edit_my_images_message(context, query)

    if query.data == "back":
        context.user_data["current_index"] -= 1
        index = context.user_data["current_index"]
        images = context.user_data["images"]
        if index < 0:
            index = len(images) - 1
        context.user_data["current_index"] = index
        await edit_my_images_message(context, query)

    if query.data == "make_public":
        db_sess = db_session.create_session()
        image = context.user_data['images'][context.user_data['current_index']]
        image.is_public = True
        image = db_sess.query(Image).filter(Image.id == image.id).first()
        image.is_public = True
        db_sess.commit()
        db_sess.close()
        await edit_my_images_message(context, query)

    if query.data == "make_private":
        db_sess = db_session.create_session()
        image = context.user_data['images'][context.user_data['current_index']]
        image.is_public = False
        image = db_sess.query(Image).filter(Image.id == image.id).first()
        image.is_public = False
        db_sess.commit()
        db_sess.close()
        await edit_my_images_message(context, query)

    if query.data == "delete":
        image = context.user_data['images'][context.user_data['current_index']]
        os.remove(image.path)
        db_sess = db_session.create_session()
        image = db_sess.query(Image).filter(Image.id == image.id).first()
        db_sess.delete(image)
        db_sess.commit()
        db_sess.close()
        context.user_data['images'].pop(context.user_data['current_index'])
        context.user_data['current_index'] += 1
        index = context.user_data['current_index']
        images = context.user_data['images']
        if index >= len(images):
            index = 0
        context.user_data['current_index'] = index
        await edit_my_images_message(context, query)


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

    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()


if __name__ == '__main__':
    generator = ImageGenerator("https://api-key.fusionbrain.ai/", config.API_KEY, config.SECRET_KEY)
    main()
