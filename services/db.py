from data.db_session import create_session
from data.images import Image
from data.image_votes import ImageVote
from data.users import User


def get_user_id(telegram_id: int) -> int:
    """
    Преобразует telegram_id в internal user_id,
    создаёт запись в users, если это первый раз.
    """
    with create_session() as db_sess:
        user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id)
            db_sess.add(user)
            db_sess.commit()
        return user.id


def add_image(user_id: int, path: str, prompt: str) -> int:
    """
    Создаёт новую запись Image и возвращает её ID.
    """
    with create_session() as db_sess:
        image = Image(user_id=user_id, path=path, prompt=prompt)
        db_sess.add(image)
        db_sess.commit()
        return image.id


def get_my_images(user_id: int):
    """
    Возвращает список объектов Image, загруженных пользователем.
    """
    with create_session() as db_sess:
        return (
            db_sess
            .query(Image)
            .filter(Image.user_id == user_id)
            .order_by(Image.id)
            .all()
        )


def get_gallery_images(user_id: int):
    """
    Возвращает публичные изображения, исключая свои.
    """
    with create_session() as db_sess:
        return (
            db_sess
            .query(Image)
            .filter(Image.is_public == True, Image.user_id != user_id)
            .order_by(Image.id)
            .all()
        )


def get_image(image_id: int) -> Image:
    """
    Возвращает объект Image по его ID.
    """
    with create_session() as db_sess:
        return db_sess.query(Image).filter(Image.id == image_id).first()


def reverse_image_privacy(image_id: int):
    """
    Переключает флаг is_public у изображения.
    """
    with create_session() as db_sess:
        image = db_sess.query(Image).filter(Image.id == image_id).first()
        if image:
            image.is_public = not image.is_public
            db_sess.commit()


def delete_image(image_id: int):
    """
    Удаляет запись изображения из БД.
    """
    with create_session() as db_sess:
        image = db_sess.query(Image).filter(Image.id == image_id).first()
        if image:
            db_sess.delete(image)
            db_sess.commit()


def vote_image(user_id: int, image_id: int, vote: int):
    """
    Ставит/снимает лайк (vote=1) или дизлайк (vote=-1)
    пользователя user_id к изображению image_id.
    """
    with create_session() as db_sess:
        image = db_sess.query(Image).filter(Image.id == image_id).first()
        existing = (
            db_sess
            .query(ImageVote)
            .filter(
                ImageVote.user_id == user_id,
                ImageVote.image_id == image_id
            )
            .first()
        )

        if existing:
            if existing.vote == vote:
                # повторный клик — снимаем голос
                if vote == 1:
                    image.like_count -= 1
                else:
                    image.dislike_count -= 1
                db_sess.delete(existing)
            else:
                # смена голоса
                if existing.vote == 1:
                    image.like_count -= 1
                    image.dislike_count += 1
                else:
                    image.dislike_count -= 1
                    image.like_count += 1
                existing.vote = vote
        else:
            # первый голос
            new_vote = ImageVote(user_id=user_id, image_id=image_id, vote=vote)
            db_sess.add(new_vote)
            if vote == 1:
                image.like_count += 1
            else:
                image.dislike_count += 1

        db_sess.commit()
