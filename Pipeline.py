import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt

def detect_objects(image_path):
    # Load YOLO model
    model = YOLO('yoloWorld.pt')

    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = model(image_rgb)[0]
    annotated_image = image_rgb.copy()

    np.random.seed(42)
    colors = np.random.randint(0, 255, size=(100, 3), dtype=np.uint8)

    class_labels = {}

    boxes = results.boxes

    return boxes, results.names, annotated_image, colors

def show_results(image_path, confidence_threshold):

    original_image = cv2.imread(image_path)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    boxes, class_names, annotated_image, colors = detect_objects(image_path)

    class_labels = {}
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])

        confidence = float(box.conf[0])

        if confidence > confidence_threshold:
            class_id = int(box.cls[0])
            class_name = class_names[class_id]

            color = colors[class_id % len(colors)].tolist()

            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
            class_labels[class_name] = color

            # Добавляем жирный текст, рисуя несколько слоев
            font_scale = 3  # Увеличиваем размер шрифта
            font = cv2.FONT_HERSHEY_SIMPLEX
            thickness = 3  # Увеличиваем толщину для жирности

            # Создаем эффект жирного текста, рисуя несколько слоев с небольшими смещениями
            for offset in range(-1, 2):
                cv2.putText(annotated_image, class_name, (x1 + offset, y1 - 10 + offset), font, font_scale, color, thickness)

    plt.figure(figsize=(15, 7))
    
    plt.subplot(1, 2, 1)
    plt.title('Original Image')
    plt.imshow(original_image)
    plt.axis('off')
    
    plt.subplot(1, 2, 2)
    plt.title('Detected Objects')
    plt.imshow(annotated_image)
    plt.axis('off')

    plt.tight_layout()
    plt.show()

show_results('88.jpg', confidence_threshold=0.2)
