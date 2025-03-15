# Импорты
import cv2
import numpy as np
from ultralytics import YOLO
import piexif
from deep_translator import GoogleTranslator
from PIL import Image
import io

# Класс ImageProcessor
class ImageProcessor:
    def __init__(self, text):
        self.model = YOLO('yolov8x-worldv2.pt')
        self.errors_not_found = text
    
    def translate_to_russian(self, class_name):
        return GoogleTranslator(source='en', target='ru').translate(class_name)

    def detect_objects(self, image_bytes):
        image = Image.open(io.BytesIO(image_bytes))
        image_rgb = np.array(image.convert("RGB"))

        results = self.model(image_rgb)[0]
        annotated_image = image_rgb.copy()

        np.random.seed(42)
        colors = np.random.randint(0, 255, size=(100, 3), dtype=np.uint8)

        boxes = results.boxes

        return boxes, results.names, annotated_image, colors

    def add_metadata_to_image(self, image_bytes, detections, original_image_bytes):
        class_names_str = ", ".join(detections["objects"])
        print(f"Detected objects: {class_names_str}")

        # Формируем строку из оригинальных и исправленных слов
        errors_str = ""
        original = ""
        corrected = ""
        for key in self.errors_not_found:
            original += f"{self.errors_not_found[key]['original']}, "
            corrected += f"{self.errors_not_found[key]['corrected']}, "
            errors_str += f"{original} : {corrected}, "
        errors_str = errors_str.rstrip(", ")  # Убираем последнюю запятую и пробел
        print(f"Errors not found: {errors_str}")

        image = Image.open(io.BytesIO(image_bytes))

        original_image = Image.open(io.BytesIO(original_image_bytes))
        exif_data = original_image.info.get("exif", None)

        if exif_data:
            overwriting_meta = piexif.load(exif_data)
        else:
            overwriting_meta = piexif.load(piexif.dump({}))

        print(f"EXIF before: {overwriting_meta}")

        # Записываем обнаруженные объекты в поле Make
        overwriting_meta["0th"][piexif.ImageIFD.Make] = class_names_str.encode('utf-8')
        # Записываем errors_not_found в поле Model
        overwriting_meta["0th"][piexif.ImageIFD.Model] =  original.encode('utf-8')# Переведённые названия
        overwriting_meta["0th"][piexif.ImageIFD.Software] = corrected.encode('utf-8')  

        print(f"EXIF after: {overwriting_meta}")

        exif_bytes = piexif.dump(overwriting_meta)

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', exif=exif_bytes)
        return img_byte_arr.getvalue()

    def process_image(self, image_bytes, confidence_threshold=0.2):
        original_image = Image.open(io.BytesIO(image_bytes))
        original_image_rgb = np.array(original_image.convert("RGB"))

        boxes, class_names, annotated_image, colors = self.detect_objects(image_bytes)

        detections = {"objects": []}

        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            confidence = float(box.conf[0])
            if confidence > confidence_threshold:
                class_id = int(box.cls[0])
                class_name = class_names[class_id]

                translated_name = self.translate_to_russian(class_name)

                print(class_name + " " + translated_name)

                color = colors[class_id % len(colors)].tolist()
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)

                font_scale = 2
                font = cv2.FONT_HERSHEY_SIMPLEX
                thickness = 2

                for offset in range(-1, 2):
                    cv2.putText(annotated_image, class_name, (x1 + offset, y1 - 10 + offset), font, font_scale, color, thickness)

                detections["objects"].append(translated_name)
                
        img_byte_arr = io.BytesIO()
        Image.fromarray(annotated_image).save(img_byte_arr, format='JPEG')

        annotated_image_bytes = img_byte_arr.getvalue()

        # Добавляем метаданные с информацией о классах объектов и errors_not_found
        updated_image_bytes = self.add_metadata_to_image(annotated_image_bytes, detections, image_bytes)
        
        return updated_image_bytes

    def get_image_with_annotations(self, image_bytes, confidence_threshold=0.2):
        return self.process_image(image_bytes, confidence_threshold)