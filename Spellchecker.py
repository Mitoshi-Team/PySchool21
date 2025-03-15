from pyaspeller import YandexSpeller
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextSpellChecker:
    def __init__(self, lang="ru"):
        """
        Инициализация проверяющего модуля.
        :param lang: Язык для проверки (по умолчанию русский, "ru").
        """
        try:
            # Поддерживаемые языки: "ru", "en", "uk"
            if lang not in ["ru", "en", "uk"]:
                raise ValueError(f"Неподдерживаемый язык: {lang}. Используйте 'ru', 'en' или 'uk'.")
            self.speller = YandexSpeller(lang=lang)
            logger.info(f"Yandex.Speller успешно инициализирован для языка: {lang}")
        except Exception as e:
            logger.error(f"Ошибка при инициализации Yandex.Speller: {e}")
            raise

    def check_and_correct(self, text):
        """
        Проверка текста на ошибки и его исправление.
        :param text: Входной текст для проверки.
        :return: Исправленный текст или оригинальный, если ошибок нет.
        """
        if not isinstance(text, str):
            logger.error("Входной текст должен быть строкой!")
            raise ValueError("Текст должен быть строкой.")

        if not text.strip():
            logger.warning("Передан пустой текст.")
            return text

        try:
            corrected_text = self.speller.spelled(text)
            logger.info(f"Текст успешно проверен. Оригинал: '{text}', Исправлено: '{corrected_text}'")
            return corrected_text
        except Exception as e:
            logger.error(f"Ошибка при проверке текста: {e}")
            return text

    def get_errors(self, text):
        """
        Получение списка ошибок в тексте без исправления.
        :param text: Входной текст.
        :return: Список словарей с информацией об ошибках.
        """
        try:
            errors = self.speller.spell(text)
            return list(errors)
        except Exception as e:
            logger.error(f"Ошибка при получении списка ошибок: {e}")
            return []

# Пример использования
if __name__ == "__main__":
    # Создаём экземпляр проверяющего модуля
    spell_checker = TextSpellChecker(lang="ru")  # Только русский

    # Тестовый текст
    input_text = "Привет, как деал? Ths is a tst."

    # Проверяем и исправляем текст
    corrected_text = spell_checker.check_and_correct(input_text)
    print(f"Оригинальный текст: {input_text}")
    print(f"Исправленный текст: {corrected_text}")

    # Получаем список ошибок
    errors = spell_checker.get_errors(input_text)
    if errors:
        print("\nНайденные ошибки:")
        for error in errors:
            print(f"Слово: '{error['word']}', Варианты исправления: {error['s']}")
    else:
        print("Ошибок не найдено.")