class StatusCodeIsNotCorrect(Exception):
    """Статус код не соответствует ожиданию."""

    pass


class NoHomeworks(Exception):
    """Нету домашний работы."""

    pass


class NoCorrectRespond(Exception):
    """Ответ API не соответствует ожиданию."""

    pass


class EndpointConnection(Exception):
    """Ошибка во время подключение к эндпойнту."""

    pass


class TokensAreNotCorrect(Exception):
    """Отсутствие обязательных переменных окружения."""

    pass
