from telegram import InputMediaPhoto
from services import db
from utils import image_util
from keyboards import (
    get_my_image_keyboard,
    get_gallery_keyboard,
    get_image_keyboard,
    get_confirm_delete_keyboard
)


async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "cancel_write_prompt":
        context.user_data['waiting_for_prompt'] = False
        await query.message.delete()
        return

    data = query.data.split(":")
    action = data[0]
    if action in ("img_like", "img_dislike"):
        scope = data[1]
        identifier = int(data[2])
        user_id = db.get_user_id(update.effective_user.id)

        if scope == "my":
            images = db.get_my_images(user_id)
            image = images[identifier]
        elif scope == "gallery":
            images = db.get_gallery_images(user_id)
            image = images[identifier]
        else:
            image = db.get_image(identifier)

        vote_value = 1 if action == "img_like" else -1
        db.vote_image(user_id, image.id, vote_value)
        updated = db.get_image(image.id)

        if scope == "my":
            kb = get_my_image_keyboard(
                updated.like_count,
                updated.dislike_count,
                updated.is_public,
                identifier
            )
        elif scope == "gallery":
            kb = get_gallery_keyboard(
                updated.like_count,
                updated.dislike_count,
                identifier
            )
        else:
            kb = get_image_keyboard(
                updated.like_count,
                updated.dislike_count,
                updated.is_public,
                updated.id
            )

        await query.message.edit_reply_markup(reply_markup=kb)
        return
    if action == "img_next":
        await navigate_images(update, context, +1, data[1])
        return

    if action == "img_back":
        await navigate_images(update, context, -1, data[1])
        return

    if action == "img_toggle":
        mode = data[1]
        if mode == "my":
            user_id = db.get_user_id(update.effective_user.id)
            images = db.get_my_images(user_id)
            idx = int(data[2])
            image = images[idx]
            db.reverse_image_privacy(image.id)
            image.is_public = not image.is_public
            await edit_my_images_message(context, query, idx, image)
        else:
            image_id = int(data[2])
            db.reverse_image_privacy(image_id)
            await edit_image_message(context, query, image_id)
        return

    if data[0] == "img_confirm_delete":
        chat_id = update.effective_chat.id
        message_id = query.message.id
        confirm_delete_keyboard = get_confirm_delete_keyboard(int(data[2]), data[1], chat_id, message_id)
        await query.message.reply_text("Вы точно хотите удалить это изображение?",
                                       reply_markup=confirm_delete_keyboard)

    if data[0] == 'reject':
        await query.message.delete()

    if action == "img_delete":
        mode = data[1]
        if mode == "my":
            await navigate_images(update, context, +1, "my")
            user_id = db.get_user_id(update.effective_user.id)
            images = db.get_my_images(user_id)
            idx = int(data[2])
            image = images[idx]
            db.delete_image(image.id)
            image_util.delete_image(image.path)
        else:
            if mode == "gallery":
                image_id = db.get_gallery_images(db.get_user_id(update.effective_user.id))[int(data[2])].id
            else:
                image_id = int(data[2])
            image = db.get_image(image_id)
            db.delete_image(image_id)
            image_util.delete_image(image.path)
            await query.message.delete()
            await context.bot.delete_message(chat_id=int(data[3]), message_id=int(data[4]))
        return


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
        img = f.read()
    await query.message.edit_media(
        media=InputMediaPhoto(media=img, caption=image.prompt),
        reply_markup=get_my_image_keyboard(
            image.like_count,
            image.dislike_count,
            image.is_public,
            index
        )
    )


async def edit_gallery_message(context, query, index, image):
    with open(image.path, "rb") as f:
        img = f.read()
    await query.message.edit_media(
        media=InputMediaPhoto(media=img, caption=image.prompt),
        reply_markup=get_gallery_keyboard(
            image.like_count,
            image.dislike_count,
            index
        )
    )


async def edit_image_message(context, query, image_id):
    image = db.get_image(image_id)
    with open(image.path, "rb") as f:
        img = f.read()
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=img,
            caption=f"Изображение по запросу: {image.prompt}"
        ),
        reply_markup=get_image_keyboard(
            image.like_count,
            image.dislike_count,
            image.is_public,
            image_id
        )
    )
