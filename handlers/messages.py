from io import BytesIO

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from services.image_generator import generate_image


async def start_generation(update, context):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data="cancel_write_prompt")]])
    await update.message.reply_text("Введите запрос", reply_markup=keyboard)
    context.user_data['waiting_for_prompt'] = True


async def get_prompt(update, context):
    if not context.user_data.get('waiting_for_prompt'):
        await update.message.reply_text("Я вас не понял. Используйте меню или команды.")
        return

    context.user_data['waiting_for_prompt'] = False

    document = update.message.document
    text = update.message.text

    if document:
        if document.file_name.lower().endswith(".txt"):
            file = await document.get_file()
            bio = BytesIO()
            await file.download_to_memory(bio)
            prompt = bio.getvalue().decode("utf-8").strip()
        else:
            await update.message.reply_text("Поддерживаются только файлы .txt")
            return
    elif text:
        prompt = text.strip()
    else:
        await update.message.reply_text("Пришлите текстовый файл (.txt) или введите запрос текстом.")
        return

    if prompt:
        await generate_image(prompt, update, context)
    else:
        await update.message.reply_text("Запрос не может быть пустым.")
