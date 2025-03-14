import cv2
import numpy as np
from ultralytics import YOLO
import matplotlib.pyplot as plt
#ddf
def detect_objects(image_path):
    model = YOLO('yolov8x.pt')

    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    results = model(image_rgb)[0]
    annotated_image = image_rgb.copy()

    np.random.seed(42)
    colors = np.random.randint(0, 255, size=(100, 3), dtype=np.uint8)

    class_labels = {}

    boxes = results.boxes

    return boxes, results.names, annotated_image, colors

def get_detected_objects(image_path, confidence_threshold=0.5):
    boxes, class_names, annotated_image, colors = detect_objects(image_path)
    
    detected_objects = [] 
    
    for box in boxes:
        confidence = float(box.conf[0])
        if confidence > confidence_threshold:
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            class_id = int(box.cls[0])
            class_name = class_names[class_id]

            detected_objects.append({
                'class_name': class_name,
                'confidence': confidence,
                'coordinates': (x1, y1, x2, y2),
                'color': colors[class_id % len(colors)].tolist()
            })
    
    return detected_objects

def show_detected_objects(image_path, confidence_threshold=0.5):
    detected_objects = get_detected_objects(image_path, confidence_threshold)
    original_image = cv2.imread(image_path)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    annotated_image = original_image.copy()

    for obj in detected_objects:
        x1, y1, x2, y2 = obj['coordinates']
        color = obj['color']
        cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(annotated_image, f'{obj["class_name"]}: {obj["confidence"]:.2f}',
                    (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    plt.figure(figsize=(10, 10))
    plt.imshow(annotated_image)
    plt.title(f'Detected Objects (Confidence > {confidence_threshold})')
    plt.axis('off')
    plt.show()

def print_detected_objects(image_path, confidence_threshold=0.5):
    detected_objects = get_detected_objects(image_path, confidence_threshold)

    for obj in detected_objects:
        print(f'Object: {obj["class_name"]}, Confidence: {obj["confidence"]:.2f}, Coordinates: {obj["coordinates"]}')


show_detected_objects('88.jpg', confidence_threshold=0.2)
