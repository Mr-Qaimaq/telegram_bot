import logging
import os
import time
import requests
import telegram
import exceptions

from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    filename='homework.log',
    level=logging.DEBUG,
    filemode='w',
    encoding='UTF-8',
)

log_console_formatter = '%(asctime)s [%(levelname)s] %(message)s'

console_handler = logging.StreamHandler()
# console_handler.setLevel(level=logging.ERROR)
# console_handler.setFormatter(logging.Formatter(log_console_formatter))

homework_status_dict = {}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправка сообщений на телеграм."""
    success = bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=message,
    )

    if success:
        logging.info('Удачная отправка сообщения')
    else:
        logging.error('Сбой при отправке сообщения')


def get_api_answer(current_timestamp):
    """Получаем ответ от API."""
    # timestamp = current_timestamp or int(time.time())
    params = {'from_date': current_timestamp}

    homework_status = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if homework_status.status_code != 200:
        error_message = 'Эндпоинт недоступен'
        logging.error(error_message)
        raise exceptions.StatusCodeIsNotCorrect(error_message)

    return homework_status.json()


def check_response(response):
    """Проверяем ответ от API на корректность."""
    if response is None:
        raise exceptions.NoCorrectRespond('Ответ API не корректен')

    if type(response) is not dict:
        raise TypeError('API вернул не словарь')

    if 'homeworks' not in response:
        error_message = 'Отсутствие ожидаемых ключей в ответе API'
        logging.error(error_message)
        raise KeyError(error_message)

    if type(response.get('homeworks')) is not list:
        raise TypeError('Домашние задания не являются списоком')

    return response.get('homeworks')


def parse_status(homework):
    """Извлекает из информации статус домашней работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')

    if homework_status not in HOMEWORK_STATUSES.keys():
        error_message = (
            'Недокументированный статус домашней работы,'
            'обнаруженный в ответе API'
        )
        logging.error(error_message)
        raise KeyError(error_message)

    verdict = HOMEWORK_STATUSES[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяем токены."""
    if (
        PRACTICUM_TOKEN is None
        or TELEGRAM_CHAT_ID is None
        or TELEGRAM_TOKEN is None
    ):
        return False
    return True


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Отсутствие обязательных переменных окружения')

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)

            if not homeworks:
                error_message = 'Новые статусы отсутствуют, ждем 10 мин'
                logging.error(error_message)
                raise exceptions.NoHomeworks(error_message)

            for homework in homeworks:
                message = parse_status(homework)
                send_message(bot, message)

            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logging.error(message)
            time.sleep(RETRY_TIME)
        else:
            logging.error('Что-то пошло не так')


if __name__ == '__main__':
    main()
