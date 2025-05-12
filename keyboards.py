from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

main_menu_keyboard = ReplyKeyboardMarkup(
    [
        ["🎨 Создать изображение"],
        ["🖼 Мои изображения"],
        ["🌍 Галерея"]
    ],
    resize_keyboard=True
)


def get_my_image_keyboard(
        like_count: int,
        dislike_count: int,
        is_public: bool,
        index: int
) -> InlineKeyboardMarkup:
    public_text = "🔥 Опубликовать" if not is_public else "🤫 Скрыть"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⬅️ Назад",
                    callback_data=f"img_back:my:{index}"
                ),
                InlineKeyboardButton(
                    f"👍 {like_count}",
                    callback_data=f"img_like:my:{index}"
                ),
                InlineKeyboardButton(
                    f"👎 {dislike_count}",
                    callback_data=f"img_dislike:my:{index}"
                ),
                InlineKeyboardButton(
                    "Вперёд ➡️",
                    callback_data=f"img_next:my:{index}"
                )
            ],
            [
                InlineKeyboardButton(
                    public_text,
                    callback_data=f"img_toggle:my:{index}"
                ),
                InlineKeyboardButton(
                    "🗑 Удалить",
                    callback_data=f"img_confirm_delete:my:{index}"
                )
            ],
        ]
    )


def get_confirm_delete_keyboard(index, mod, chat_id, message_id):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ подтверждаю", callback_data=f"img_delete:{mod}:{index}:{chat_id}:{message_id}"),
                InlineKeyboardButton("Отмена", callback_data=f"reject:{mod}:{index}")
            ]
        ]
    )
    return keyboard


def get_gallery_keyboard(
        like_count: int,
        dislike_count: int,
        index: int
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⬅️ Назад",
                    callback_data=f"img_back:gallery:{index}"
                ),
                InlineKeyboardButton(
                    f"👍 {like_count}",
                    callback_data=f"img_like:gallery:{index}"
                ),
                InlineKeyboardButton(
                    f"👎 {dislike_count}",
                    callback_data=f"img_dislike:gallery:{index}"
                ),
                InlineKeyboardButton(
                    "Вперёд ➡️",
                    callback_data=f"img_next:gallery:{index}"
                )
            ]
        ]
    )


def get_image_keyboard(
        like_count: int,
        dislike_count: int,
        is_public: bool,
        image_id: int
) -> InlineKeyboardMarkup:
    public_text = "🔥 Опубликовать" if not is_public else "🤫 Скрыть"
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    f"👍 {like_count}",
                    callback_data=f"img_like:image:{image_id}"
                ),
                InlineKeyboardButton(
                    f"👎 {dislike_count}",
                    callback_data=f"img_dislike:image:{image_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    public_text,
                    callback_data=f"img_toggle:image:{image_id}"
                ),
                InlineKeyboardButton(
                    "🗑 Удалить",
                    callback_data=f"img_confirm_delete:image:{image_id}"
                )
            ]
        ]
    )
