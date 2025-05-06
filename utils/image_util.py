import base64
import os


def decode_image(image):
    image_data = base64.b64decode(image)
    return image_data


def save_image(path, image_data):
    with open(path, mode="wb+") as file:
        file.write(image_data)


def delete_image(path):
    os.remove(path)
