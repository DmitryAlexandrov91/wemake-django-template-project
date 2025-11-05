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
EDIT_ANSWER_TEXT = 'Изменить ответ {answer_number}'
PROCESS_NEW_ANSWER_TEXT = 'Введите новый ответ:'
CANSEL_EDIT = 'Отмена'

SURVEY_START = """
Добрый день, {full_name}\n
Ответьте, пожалуйста, на вопрос:\n
<i>{question}</i>
"""
