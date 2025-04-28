from telegram import ReplyKeyboardMarkup

main_menu_keyboard = ReplyKeyboardMarkup(
    [
        ["🎨 Создать изображение"],
        ["🖼 Мои изображения"],
        ["🌍 Галерея"]
    ],
    resize_keyboard=True
)
