class StatusCodeIsNotCorrect(Exception):
    """Статус код не соответствует ожиданию."""

    pass


class NoHomeworks(Exception):
    """Нету домашний работы."""

    pass


class NoCorrectRespond(Exception):
    """Ответ API не соответствует ожиданию."""

    pass
