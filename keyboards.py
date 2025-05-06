from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

main_menu_keyboard = ReplyKeyboardMarkup(
    [
        ["🎨 Создать изображение"],
        ["🖼 Мои изображения"],
        ["🌍 Галерея"]
    ],
    resize_keyboard=True
)


def get_my_image_keyboard(like_count, dislike_count, is_public, index):
    public_text = "🔥 Опубликовать" if not is_public else "🤫 Скрыть"
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⬅️ Назад", callback_data=f"img_back:my:{index}"),
                InlineKeyboardButton(f"👍 {like_count}", callback_data="like"),
                InlineKeyboardButton(f"👎 {dislike_count}", callback_data="dislike"),
                InlineKeyboardButton("Вперёд ➡️", callback_data=f"img_next:my:{index}")
            ],
            [
                InlineKeyboardButton(public_text, callback_data=f"img_toggle:my:{index}"),
                InlineKeyboardButton("🗑 Удалить", callback_data=f"img_confirm_delete:my:{index}")
            ]
        ]
    )
    return keyboard


def get_confirm_delete_keyboard(index):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ подтверждаю", callback_data=f"img_delete:my:{index}"),
                InlineKeyboardButton("Отмена", callback_data=f"reject:my:{index}")
            ]
        ]
    )
    return keyboard


def get_gallery_keyboard(like_count, dislike_count, index):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⬅️ Назад", callback_data=f"img_back:gallery:{index}"),
                InlineKeyboardButton(f"👍 {like_count}", callback_data=f"img_like:gallery:{index}"),
                InlineKeyboardButton(f"👎 {dislike_count}", callback_data=f"img_dislike:gallery:{index}"),
                InlineKeyboardButton("Вперёд ➡️", callback_data=f"img_next:gallery:{index}")
            ]
        ]
    )
    return keyboard


def get_image_keyboard(is_public, image_id):
    public_text = "🔥 Опубликовать" if not is_public else "🤫 Скрыть"
    image_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(public_text, callback_data=f"img_toggle:image:{image_id}"),
                InlineKeyboardButton(f"🗑 Удалить", callback_data=f"img_delete:image:{image_id}")
            ]
        ]
    )
    return image_keyboard
