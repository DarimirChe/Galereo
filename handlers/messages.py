from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from services.image_generator import generate_image


async def start_generation(update, context):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data="cancel_write_prompt")]])
    await update.message.reply_text("Введите запрос", reply_markup=keyboard)
    context.user_data['waiting_for_prompt'] = True


async def get_prompt(update, context):
    if context.user_data.get('waiting_for_prompt'):
        prompt = update.message.text
        context.user_data['waiting_for_prompt'] = False
        await generate_image(prompt, update, context)
    else:
        await update.message.reply_text("Я вас не понял. Используйте меню или команды.")
