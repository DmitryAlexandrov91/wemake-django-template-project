import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('title', models.CharField(max_length=254)),
                ('description', models.TextField(blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'default_related_name': 'surveys',
                'constraints': [
                    models.CheckConstraint(
                        condition=models.Q(
                            ('end_date__gte', models.F('start_date')),
                            ('end_date__isnull', True),
                            _connector='OR',
                        ),
                        name='surveys_survey_dates_valid',
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('text', models.TextField()),
                (
                    'question_type',
                    models.CharField(
                        choices=[
                            ('ratingScale', 'Rating scale'),
                            ('score', 'Score'),
                            ('consentGiven', 'Consent given'),
                        ],
                        max_length=254,
                    ),
                ),
                (
                    'survey',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='surveys.survey',
                    ),
                ),
            ],
            options={
                'default_related_name': 'questions',
            },
        ),
        migrations.CreateModel(
            name='AnswerOption',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('text', models.TextField()),
                (
                    'question',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='surveys.question',
                    ),
                ),
            ],
            options={
                'verbose_name': 'answer option',
                'default_related_name': 'answer_options',
                'constraints': [
                    models.UniqueConstraint(
                        fields=('question', 'text'), name='unique_answer'
                    )
                ],
            },
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.UniqueConstraint(
                fields=('survey', 'text'), name='unique_question_per_survey'
            ),
        ),
        migrations.AddConstraint(
            model_name='question',
            constraint=models.CheckConstraint(
                condition=models.Q((
                    'question_type__in',
                    ['ratingScale', 'score', 'consentGiven'],
                )),
                name='surveys_question_question_type_valid',
            ),
        ),
        migrations.CreateModel(
            name='SurveyResult',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'survey',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='result',
                        to='surveys.survey',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='survey_result',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'survey result',
                'verbose_name_plural': 'survey results',
            },
        ),
        migrations.CreateModel(
            name='UserAnswer',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('text_answer', models.TextField(blank=True)),
                (
                    'question',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='user_answers',
                        to='surveys.question',
                    ),
                ),
                (
                    'selected_options',
                    models.ManyToManyField(
                        blank=True,
                        related_name='user_answers',
                        to='surveys.answeroption',
                    ),
                ),
                (
                    'survey_result',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='user_answers',
                        to='surveys.surveyresult',
                    ),
                ),
            ],
            options={
                'verbose_name': 'user answer',
                'verbose_name_plural': 'user answers',
            },
        ),
    ]
