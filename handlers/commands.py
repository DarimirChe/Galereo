from keyboards import get_my_image_keyboard, main_menu_keyboard
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
