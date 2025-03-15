import easyocr
import requests
from io import BytesIO
from PIL import Image
from pyaspeller import YandexSpeller
import logging
import re

text = {}  # Переменная text как словарь для хранения оригинального и исправленного текста

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Функция для загрузки изображения с Google Drive
def download_image_from_gdrive(url):
    try:
        file_id = url.split('/d/')[1].split('/')[0]
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        response = requests.get(download_url)
        if response.status_code != 200:
            raise Exception(f"Ошибка загрузки изображения с Google Drive. Код: {response.status_code}")
        
        image = Image.open(BytesIO(response.content))
        logger.info("Изображение успешно загружено с Google Drive")
        return image
    except Exception as e:
        logger.error(f"Ошибка при загрузке изображения: {e}")
        raise

class TextSpellChecker:
    def __init__(self):
        try:
            self.speller_ru = YandexSpeller(lang="ru")
            self.speller_en = YandexSpeller(lang="en")
            logger.info("Yandex.Speller инициализирован для языков: ru, en")
        except Exception as e:
            logger.error(f"Ошибка при инициализации Yandex.Speller: {e}")
            raise

    def detect_language(self, text):
        """Определяет язык текста на основе наличия кириллицы или латиницы"""
        if not text.strip():
            return "unknown"
        cyrillic = bool(re.search('[а-яА-ЯёЁ]', text))
        latin = bool(re.search('[a-zA-Z]', text))
        if cyrillic and not latin:
            return "ru"
        elif latin and not cyrillic:
            return "en"
        else:
            return "mixed"  

    def check_and_correct(self, text):
        if not isinstance(text, str):
            logger.error("Входной текст должен быть строкой!")
            raise ValueError("Текст должен быть строкой.")
        if not text.strip():
            logger.warning("Передан пустой текст.")
            return text

        lang = self.detect_language(text)
        try:
            if lang == "ru":
                corrected_text = self.speller_ru.spelled(text)
            elif lang == "en":
                corrected_text = self.speller_en.spelled(text)
            else:  
                words = text.split()
                corrected_words = []
                for word in words:
                    word_lang = self.detect_language(word)
                    if word_lang == "ru":
                        corrected_words.append(self.speller_ru.spelled(word))
                    elif word_lang == "en":
                        corrected_words.append(self.speller_en.spelled(word))
                    else:
                        corrected_words.append(word) 
                corrected_text = " ".join(corrected_words)

            logger.info(f"Текст проверен ({lang}). Оригинал: '{text}', Исправлено: '{corrected_text}'")
            return corrected_text
        except Exception as e:
            logger.error(f"Ошибка при проверке текста: {e}")
            return text

    def get_errors(self, text):
        lang = self.detect_language(text)
        try:
            if lang == "ru":
                errors = self.speller_ru.spell(text)
            elif lang == "en":
                errors = self.speller_en.spell(text)
            else:  # mixed
                errors = []
                words = text.split()
                for word in words:
                    word_lang = self.detect_language(word)
                    if word_lang == "ru":
                        errors.extend(self.speller_ru.spell(word))
                    elif word_lang == "en":
                        errors.extend(self.speller_en.spell(word))
            return list(errors)
        except Exception as e:
            logger.error(f"Ошибка при получении списка ошибок: {e}")
            return []

def process_image_text(google_drive_url):
    # Инициализация EasyOCR
    reader = easyocr.Reader(['en', 'ru'])
    spell_checker = TextSpellChecker()
    
    # Загрузка и распознавание
    try:
        image = download_image_from_gdrive(google_drive_url)
        result = reader.readtext(image)
        
        if not result:
            logger.warning("Текст на изображении не обнаружен")
            print("Текст на изображении не обнаружен")
            return
        
        # Обработка распознанного текста
        print("\nРаспознанный текст и его исправление:")
        for i, detection in enumerate(result):
            original_text = detection[1]
            detected_lang = spell_checker.detect_language(original_text)
            corrected_text = spell_checker.check_and_correct(original_text)
            
            # Запись в переменную text
            text[f"text_{i}"] = {
                "original": original_text,
                "corrected": corrected_text
            }
            
            print(f"\nОпределённый язык: {detected_lang}")
            print(f"Оригинальный текст: {original_text}")
            print(f"Исправленный текст: {corrected_text}")
            
            errors = spell_checker.get_errors(original_text)
            if errors:
                print("Найденные ошибки:")
                for error in errors:
                    print(f"Слово: '{error['word']}', Варианты: {error['s']}")
            else:
                print("Ошибок не найдено.")

        return text
                
    except Exception as e:
        logger.error(f"Ошибка в процессе обработки: {e}")
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    google_drive_url = "https://drive.google.com/file/d/1osQl41JRHcphGVk7DeRw5yDq1sFQ1b_J/view?usp=sharing"
    processed_text = process_image_text(google_drive_url)
    print("\nСодержимое переменной text:")
    print(processed_text)