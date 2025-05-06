from telegram import InputMediaPhoto

from keyboards import *


async def handle_callback(update, context):
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
        #    db_sess = db_session.create_session()
        #    images = context.user_data['images']
        #    image = images[context.user_data['current_index']]
        #    image.is_public = True
        #    image = db_sess.query(Image).filter(Image.id == image.id).first()
        #    image.is_public = True
        #    db_sess.commit()
        #    db_sess.close()
        await edit_my_images_message(context, query)

    if query.data == "make_private":
        #    db_sess = db_session.create_session()
        #    images = context.user_data['images']
        #    image = images[context.user_data['current_index']]
        #    image.is_public = False
        #    image = db_sess.query(Image).filter(Image.id == image.id).first()
        #    image.is_public = False
        #    db_sess.commit()
        #    db_sess.close()
        await edit_my_images_message(context, query)

    if query.data == "delete":
        #    image = context.user_data['images'][context.user_data['current_index']]
        #    os.remove(image.path)
        #    db_sess = db_session.create_session()
        #    image = db_sess.query(Image).filter(Image.id == image.id).first()
        #    db_sess.delete(image)
        #    db_sess.commit()
        #    db_sess.close()
        #    context.user_data['images'].pop(context.user_data['current_index'])
        #    context.user_data['current_index'] += 1
        #    index = context.user_data['current_index']
        #    images = context.user_data['images']
        #    if index >= len(images):
        #        index = 0
        #    context.user_data['current_index'] = index
        await edit_my_images_message(context, query)

    if query.data == "make_public_1" and False:  # and False это затычка, потому что в этом условии и двух следующих код не работает и выдаёт исключение
        #    db_sess = db_session.create_session()
        #    images = context.user_data['images']
        #    image = images[context.user_data['current_index']]
        #    image.is_public = True
        #    image = db_sess.query(Image).filter(Image.id == image.id).first()
        #    image.is_public = True
        #    db_sess.commit()
        #    db_sess.close()
        await edit_image_message(context, query)

    if query.data == "make_private_1" and False:
        #    db_sess = db_session.create_session()
        #    images = context.user_data['images']
        #    image = images[context.user_data['current_index']]
        #    image.is_public = False
        #    image = db_sess.query(Image).filter(Image.id == image.id).first()
        #    image.is_public = False
        #    db_sess.commit()
        #    db_sess.close()
        await edit_image_message(context, query)

    if query.data == "delete_1" and False:
        #    image = context.user_data['images'][context.user_data['current_index']]
        #    print("Удаляем изображение: ", image.path)
        #    os.remove(image.path)
        #    db_sess = db_session.create_session()
        #    image = db_sess.query(Image).filter(Image.id == image.id).first()
        #    db_sess.delete(image)
        #    db_sess.commit()
        #    db_sess.close()
        #    context.user_data['images'] = []
        await query.message.delete()
        # await edit_my_images_message(context, query)


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


async def edit_image_message(context, query):
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
        reply_markup=get_image_keyboard(image.is_public)
    )
