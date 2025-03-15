import cv2
import numpy as np
from ultralytics import YOLO
import io
from PIL import Image
from googletrans import Translator
import piexif


class ImageProcessor:
    def __init__(self):
        self.model = YOLO('yolov8x-worldv2.pt')
        self.translator = Translator()

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

        image = Image.open(io.BytesIO(image_bytes))

        original_image = Image.open(io.BytesIO(original_image_bytes))
        exif_data = original_image.info.get("exif", None)

        if exif_data:
            overwriting_meta = piexif.load(exif_data)
        else:
            overwriting_meta = piexif.load(piexif.dump({}))

        print(f"EXIF before: {overwriting_meta}")

        overwriting_meta["0th"][piexif.ImageIFD.Make] = class_names_str.encode('utf-8')

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

                translated_class_name = self.translator.translate(class_name, src='en', dest='ru').text

                color = colors[class_id % len(colors)].tolist()
                cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)

                font_scale = 3
                font = cv2.FONT_HERSHEY_SIMPLEX
                thickness = 10

                for offset in range(-1, 2):
                    cv2.putText(annotated_image, translated_class_name, (x1 + offset, y1 - 10 + offset), font, font_scale, color, thickness)

                detections["objects"].append(translated_class_name)
                

        img_byte_arr = io.BytesIO()
        Image.fromarray(annotated_image).save(img_byte_arr, format='JPEG')

        annotated_image_bytes = img_byte_arr.getvalue()

        # Добавляем метаданные с информации о классах объектов
        updated_image_bytes = self.add_metadata_to_image(annotated_image_bytes, detections, image_bytes)
        
        return updated_image_bytes

    def get_image_with_annotations(self, image_bytes, confidence_threshold=0.2):
        return self.process_image(image_bytes, confidence_threshold)


processor = ImageProcessor()

with open('88.jpg', 'rb') as f:
    image_bytes = f.read()

updated_image_bytes = processor.get_image_with_annotations(image_bytes)

with open('88-р.jpg', 'wb') as f:
    f.write(updated_image_bytes)
