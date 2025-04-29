from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

main_menu_keyboard = ReplyKeyboardMarkup(
    [
        ["🎨 Создать изображение"],
        ["🖼 Мои изображения"],
        ["🌍 Галерея"]
    ],
    resize_keyboard=True
)


def get_my_image_keyboard(like_count, dislike_count, is_public):
    public_text = "🔥 Опубликовать" if not is_public else "🤫 Скрыть"
    public_callback = "make_public" if not is_public else "make_private"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("⬅️ Назад", callback_data="back"),
                InlineKeyboardButton(f"👍 {like_count}", callback_data="like"),
                InlineKeyboardButton(f"👎 {dislike_count}", callback_data="dislike"),
                InlineKeyboardButton("➡️ Вперёд", callback_data="next")
            ],
            [
                InlineKeyboardButton(public_text, callback_data=public_callback),
                InlineKeyboardButton("🗑 Удалить", callback_data="delete")
            ]
        ]
    )
    return keyboard


def get_image_keyboard(is_public):
    public_text = "🔥 Опубликовать" if not is_public else "🤫 Скрыть"
    public_callback = "make_public_1" if not is_public else "make_private_1"
    image_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(public_text, callback_data=public_callback),
                InlineKeyboardButton(f"🗑 Удалить", callback_data="delete_1")
            ]
        ]
    )
    return image_keyboard
