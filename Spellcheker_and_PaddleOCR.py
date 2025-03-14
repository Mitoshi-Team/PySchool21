import requests
from paddleocr import PaddleOCR
from pyaspeller import YandexSpeller
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация OCR для обоих языков
ocr_ru = PaddleOCR(use_angle_cls=True, lang='ru')
ocr_en = PaddleOCR(use_angle_cls=True, lang='en')

# Класс Spellchecker
class TextSpellChecker:
    def __init__(self, lang="ru"):
        if lang not in ["ru", "en", "uk"]:
            raise ValueError(f"Неподдерживаемый язык: {lang}")
        self.speller = YandexSpeller(lang=lang)
        logger.info(f"Yandex.Speller инициализирован для языка: {lang}")

    def check_and_correct(self, text):
        if not isinstance(text, str) or not text.strip():
            return text
        try:
            corrected_text = self.speller.spelled(text)
            logger.info(f"Текст проверен. Оригинал: '{text}', Исправлено: '{corrected_text}'")
            return corrected_text
        except Exception as e:
            logger.error(f"Ошибка проверки: {e}")
            return text

# Функция обработки изображения
def process_image(file_id):
    download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
    output_path = 'downloaded_image.jpg'
    
    response = requests.get(download_url)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(response.content)
        logger.info(f"Изображение скачано: {output_path}")
    else:
        logger.error(f"Ошибка скачивания: {response.status_code}")
        return None

    # Распознавание текста
    result_ru = ocr_ru.ocr(output_path, cls=True)
    result_en = ocr_en.ocr(output_path, cls=True)
    
    recognized_texts = []
    if result_ru and result_ru[0]:
        recognized_texts.extend([line[1][0] for line in result_ru[0]])
    if result_en and result_en[0]:
        recognized_texts.extend([line[1][0] for line in result_en[0]])
    return recognized_texts if recognized_texts else None

# Определение языка
def detect_language(text):
    if any(ord(char) > 127 for char in text):
        return "ru"
    return "en"

# Основная логика
if __name__ == "__main__":
    spell_checker_ru = TextSpellChecker(lang="ru")
    spell_checker_en = TextSpellChecker(lang="en")
    
    file_id = '1VxZ2qycBBpehhSlkqwbAeesnjxHiu_WS'

    recognized_texts = process_image(file_id)
    
    if recognized_texts:
        for idx, text in enumerate(recognized_texts):
            lang = detect_language(text)
            spell_checker = spell_checker_ru if lang == "ru" else spell_checker_en
            corrected_text = spell_checker.check_and_correct(text)
            print(f"Строка {idx + 1}: Язык: {lang}, Оригинал: {text}, Исправлено: {corrected_text}")
    else:
        print("Текст не распознан.")