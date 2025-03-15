import logging
from io import BytesIO
from PIL import Image
from Spellcheker_and_Easyocr import process_image_text, download_image_from_gdrive
from cliv import ImageProcessor


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main(google_drive_url):
    try:
        # Извлечение и исправление текста с изображения
        logger.info("Запуск обработки текста с изображения...")
        image = download_image_from_gdrive(google_drive_url) 
        get_text = process_image_text(google_drive_url) 

        print(get_text)
        
        # Преобразование изображения в байты для дальнейшей обработки
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='JPEG')
        image_bytes = img_byte_arr.getvalue()

        # Шаг 3: Детекция объектов и аннотирование изображения
        logger.info("Запуск детекции объектов на изображении...")
        processor = ImageProcessor(get_text)
        updated_image_bytes = processor.get_image_with_annotations(image_bytes)

        # Шаг 4: Сохранение результата
        output_path = "annotated_image_with_text.jpg"
        with open(output_path, 'wb') as f:
            f.write(updated_image_bytes)
        logger.info(f"Результат сохранён в файл: {output_path}")

    except Exception as e:
        logger.error(f"Ошибка в процессе выполнения: {e}")
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    # Прямая ссылка на Google Drive
    google_drive_url = "https://drive.google.com/file/d/1y-7BglW-1u-EqSGc0qhKSCoUbddzDtBF/view?usp=sharing"
    
    # Запуск процесса
    main(google_drive_url)