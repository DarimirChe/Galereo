import asyncio
from datetime import datetime

import requests
import json

import config
from keyboards import get_image_keyboard
from services import db
from utils import image_util


class ImageGenerator:
    def __init__(self, url: str, api_key: str, secret_key: str):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self) -> str:
        response = requests.get(
            self.URL + 'key/api/v1/pipelines',
            headers=self.AUTH_HEADERS
        )
        data = response.json()
        return data[0]['id']

    def generate(
            self,
            prompt: str,
            pipeline: str,
            images: int = 1,
            width: int = 1024,
            height: int = 1024
    ) -> str:
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": prompt
            }
        }
        files = {
            'pipeline_id': (None, pipeline),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(
            self.URL + 'key/api/v1/pipeline/run',
            headers=self.AUTH_HEADERS,
            files=files
        )
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id: str):
        response = requests.get(
            self.URL + 'key/api/v1/pipeline/status/' + request_id,
            headers=self.AUTH_HEADERS
        )
        data = response.json()
        if data.get('status') == 'DONE':
            return data['result']['files']
        return None


generator = ImageGenerator(
    url="https://api-key.fusionbrain.ai/",
    api_key=config.API_KEY,
    secret_key=config.SECRET_KEY
)


async def generate_image(prompt: str, update, context):
    pipeline_id = generator.get_pipeline()
    uuid = generator.generate(prompt, pipeline_id)
    sent_message = await update.message.reply_text("Изображение генерируется...")
    delay = 5
    images = None
    for i in range(10, 0, -1):
        images = generator.check_generation(uuid)
        if images is not None:
            break
        await sent_message.edit_text(f"Изображение генерируется. Осталось ~{i * delay} с.")
        await asyncio.sleep(delay)
    await sent_message.edit_text("Изображение отправляется...")
    user = update.effective_user
    telegram_id = user.id
    timestamp = datetime.now().strftime('%d-%m-%Y_%H-%M-%S')
    path = f"data/images/image_{telegram_id}_{timestamp}.jpg"
    image_bytes = image_util.decode_image(images[0])
    image_util.save_image(path, image_bytes)
    user_id = db.get_user_id(telegram_id)
    db.add_image(user_id, path, prompt)
    image_id = sorted(
        db.get_my_images(user_id),
        key=lambda img: img.id,
        reverse=True
    )[0].id
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=image_bytes,
        caption=f"Изображение по запросу: {prompt}",
        reply_markup=get_image_keyboard(
            like_count=0,
            dislike_count=0,
            is_public=False,
            image_id=image_id
        )
    )

    await sent_message.delete()
