from telegram import InputMediaPhoto
from services import db
from utils import image_util
from keyboards import *


async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "cancel_write_prompt":
        context.user_data['waiting_for_prompt'] = False
        await query.message.delete()

    data = query.data.split(":")
    if data[0] == "img_next":
        await navigate_images(update, context, +1, data[1])

    if data[0] == "img_back":
        await navigate_images(update, context, -1, data[1])

    if data[0] == "img_toggle":
        if data[1] == "my":
            telegram_id = update.effective_user.id
            user_id = db.get_user_id(telegram_id)
            images = db.get_my_images(user_id)
            index = int(data[2])
            image = images[index]
            db.reverse_image_privacy(image.id)
            image.is_public = not image.is_public
            await edit_my_images_message(context, query, index, image)
        else:
            image_id = int(data[2])
            db.reverse_image_privacy(image_id)
            await edit_image_message(context, query, image_id)

    if data[0] == "img_confirm_delete":
        if data[1] == "my":
            confirm_delete_keyboard = get_confirm_delete_keyboard(int(data[2]))
            await update.message.reply_text("Вы точно хотите удалить это изображение?",
                                            reply_markup=confirm_delete_keyboard)

    if data[0] == "img_delete":
        if data[1] == "my":
            telegram_id = update.effective_user.id
            user_id = db.get_user_id(telegram_id)
            images = db.get_my_images(user_id)
            index = int(data[2])
            image = images[index]
            db.delete_image(image.id)
            image_util.delete_image(image.path)
            await navigate_images(update, context, +1, data[1])
        else:
            image_id = int(data[2])
            image = db.get_image(image_id)
            db.delete_image(image_id)
            image_util.delete_image(image.path)
            await query.message.delete()


async def navigate_images(update, context, direction, mode):
    query = update.callback_query
    telegram_id = update.effective_user.id
    user_id = db.get_user_id(telegram_id)

    if mode == "my":
        images = db.get_my_images(user_id)
    else:
        images = db.get_gallery_images(user_id)

    index = int(query.data.split(":")[2]) + direction
    index %= len(images)

    if mode == "my":
        await edit_my_images_message(context, query, index, images[index])
    else:
        await edit_gallery_message(context, query, index, images[index])


async def edit_my_images_message(context, query, index, image):
    with open(image.path, "rb") as f:
        image_bytes = f.read()

    await query.message.edit_media(
        media=InputMediaPhoto(
            media=image_bytes,
            caption=image.prompt
        ),
        reply_markup=get_my_image_keyboard(
            image.like_count,
            image.dislike_count,
            image.is_public,
            index
        )
    )


async def edit_gallery_message(context, query, index, image):
    with open(image.path, "rb") as f:
        image_bytes = f.read()

    await query.message.edit_media(
        media=InputMediaPhoto(
            media=image_bytes,
            caption=image.prompt
        ),
        reply_markup=get_gallery_keyboard(
            image.like_count,
            image.dislike_count,
            index
        )
    )


async def edit_image_message(context, query, image_id):
    image = db.get_image(image_id)
    with open(image.path, "rb") as f:
        image_bytes = f.read()

    await query.message.edit_media(
        media=InputMediaPhoto(
            media=image_bytes,
            caption=f"Изображение по запросу: {image.prompt}"
        ),
        reply_markup=get_image_keyboard(image.is_public, image_id)
    )
