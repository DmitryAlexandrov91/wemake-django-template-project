SURVEY_RESULTS_TEMPLATE = """
📋 Опрос <b>{survey_title}</b>
<i>редактирование доступно до {end_date}</i>
{answers}
"""

ANSWER_TEMPLATE = """
<b>Вопрос №{question_number}:</b> <i>{question_text}</i>
Ваш ответ: <i>{answer_text}</i>
"""

NO_ANSWERS = 'Ответов нет'
EDIT_ANSWER_TEXT = 'Изменить №{answer_number}'
PROCESS_NEW_ANSWER_TEXT = 'Введите новый ответ:'
CANSEL_EDIT = 'Отмена'


SUGGESTION_SAVED = '✅ Спасибо! Ваше предложение сохранено.'
SUGGESTION_REQUEST = '✏️ Пожалуйста, напишите своё предложение.'
NO_USERNAME = '❗️ Установите Tg username перед отправкой предложений.'
NO_USER = '❗️ He удалось определить пользователя.'
NO_TEXT = '❗️ Сообщение не содержит текста.'
EMPTY_SUGGESTION = 'Вы ничего не написали.'

SURVEY_COMPLITED = """
Вопросов без ответов не найдено
"""

SURVEY_START = """
Добрый день, {full_name}\n
Ответьте, пожалуйста, на вопрос:\n
<b><i>{question}</i></b>
"""

SURVEY_CONTINUE = """
Ответьте, пожалуйста, на следующий вопрос:\n
<b><i>{question}</i></b>
"""

SURVEY_STATUS_EDIT_FORBIDDEN = (
    'Текущий статус опроса не предусматривает редактирование ответов'
)
SURVEY_NOT_FOUND = 'Активный опрос не найден'
