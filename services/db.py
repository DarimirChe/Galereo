from data import db_session
from data.users import User
from data.images import Image


def get_user_id(telegram_id):
    with db_session.create_session() as db_sess:
        user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()
    return user.id


def add_user(telegram_id):
    with db_session.create_session() as db_sess:
        user = User()
        user.telegram_id = telegram_id
        db_sess.add(user)
        db_sess.commit()


def add_image(user_id, path, prompt):
    with db_session.create_session() as db_sess:
        image = Image()
        image.user_id = user_id
        image.path = path
        image.prompt = prompt
        db_sess.add(image)
        db_sess.commit()
    return image


def get_my_images(user_id):
    with db_session.create_session() as db_sess:
        images = db_sess.query(Image).filter(Image.user_id == user_id).all()
    return images


def get_gallery_images(user_id):
    with db_session.create_session() as db_sess:
        images = db_sess.query(Image).filter(Image.user_id != user_id and Image.is_public).all()
    return images


def reverse_image_privacy(image_id):
    with db_session.create_session() as db_sess:
        image = db_sess.query(Image).filter(Image.id == image_id).first()
        image.is_public = not image.is_public
        db_sess.commit()
