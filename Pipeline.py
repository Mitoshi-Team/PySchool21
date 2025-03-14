import cv2
from ultralytics import YOLO
from googletrans import Translator

# Загружаем модель YOLOv8
model = YOLO("yolov8x.pt")

# Инициализируем переводчик
translator = Translator()

def translate_to_russian(class_name):
    # Переводим название класса на русский язык
    translation = translator.translate(class_name, src='en', dest='ru')
    return translation.text

def getImage(image_path):
    image = cv2.imread(image_path)
    results = model(image_path, imgsz=1280, conf=0.1, agnostic_nms=True)
    class_names = model.names

    detected_objects = []  # Список найденных объектов

    for r in results:
        for box in r.boxes:
            class_id = int(box.cls.item())
            class_name = class_names[class_id]
            # Переводим название класса на русский
            translated_name = translate_to_russian(class_name)
            detected_objects.append(translated_name)

    return detected_objects  # Возвращаем список найденных объектов на русском

# Вызываем функцию и выводим результат
objects = getImage("images.jpg")
print("Обнаруженные объекты:", objects)
