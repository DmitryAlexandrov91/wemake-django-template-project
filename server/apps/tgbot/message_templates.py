SURVEY_RESULTS_TEMPLATE = """
📋 Опрос <b>{survey_title}</b>

{answers}
"""

ANSWER_TEMPLATE = """
<b>Вопрос №{question_number}:</b>
<i>{question_text}</i>

Ваш ответ:
<i>{answer_text}</i>
"""

NO_ANSWERS = 'Ответов нет'
EDIT_ANSWER_TEXT = 'Изменить ответ на вопрос №{answer_number}'
PROCESS_NEW_ANSWER_TEXT = 'Введите новый ответ:'
CANSEL_EDIT = 'Отмена'


SUGGESTION_SAVED = '✅ Спасибо! Ваше предложение сохранено.'
NO_USERNAME = '❗️ Установите Tg username перед отправкой предложений.'
NO_USER = '❗️ He удалось определить пользователя.'
NO_TEXT = '❗️ Сообщение не содержит текста.'
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
