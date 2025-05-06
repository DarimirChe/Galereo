from keyboards import get_my_image_keyboard, main_menu_keyboard, get_gallery_keyboard
from services.image_generator import generate_image
from services import db


async def generate_image_command(update, context):
    context.user_data['waiting_for_prompt'] = False
    if context.args:
        prompt = " ".join(context.args)
        await generate_image(prompt, update, context)
    else:
        await update.message.reply_text("Запрос не может быть пустым.")


async def help_command(update, context):
    await update.message.reply_text("/gen <запрос> -- генерация изображения по запросу.\n"
                                    "/my_images -- посмотреть свои изображения\n"
                                    "/gallery -- посмотеть галлерею")


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я Galereo-бот, могу создавать изображения по запросу. Введите /help чтобы увидеть список команд или воспользуйтесь кнопками меню",
        reply_markup=main_menu_keyboard
    )

    telegram_id = user.id
    user = db.get_user_id(telegram_id)

    if not user:  # если пользователя нет в БД то добавим его
        db.add_user(telegram_id)


async def my_images(update, context):
    user = update.effective_user
    context.user_data['waiting_for_prompt'] = False
    telegram_id = user.id

    user_id = db.get_user_id(telegram_id)
    images = db.get_my_images(user_id)

    if not images:
        await update.message.reply_text("У вас нету изображений")
        return

    with open(images[0].path, mode="rb") as img:
        image_bytes = img.read()

    my_image_keyboard = get_my_image_keyboard(
        images[0].like_count,
        images[0].dislike_count,
        images[0].is_public,
        0
    )

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=image_bytes,
        caption=images[0].prompt, reply_markup=my_image_keyboard
    )


async def gallery(update, context):
    user = update.effective_user
    context.user_data['waiting_for_prompt'] = False
    telegram_id = user.id

    user_id = db.get_user_id(telegram_id)
    images = db.get_gallery_images(user_id)

    if not images:
        await update.message.reply_text("В галерее пусто")
        return

    with open(images[0].path, mode="rb") as img:
        image_bytes = img.read()

    gallery_keyboard = get_gallery_keyboard(
        images[0].like_count,
        images[0].dislike_count,
        0
    )

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=image_bytes,
        caption=images[0].prompt,
        reply_markup=gallery_keyboard
    )
