def save_image(path, image_data):
    with open(path, mode="wb+") as file:
        file.write(image_data)