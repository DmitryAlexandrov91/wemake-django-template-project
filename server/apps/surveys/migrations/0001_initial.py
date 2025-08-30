from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    text = 'text'

    dependencies = []

    operations = [
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
                (text, models.TextField()),
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
            ],
            options={
                'default_related_name': 'question',
                'constraints': [
                    models.UniqueConstraint(
                        fields=(text,), name='unique_question'
                    ),
                    models.CheckConstraint(
                        condition=models.Q((
                            'question_type__in',
                            ['ratingScale', 'score', 'consentGiven'],
                        )),
                        name='surveys_question_question_type_valid',
                    ),
                ],
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
                (text, models.TextField()),
                (
                    'question',
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        to='surveys.question',
                    ),
                ),
            ],
            options={
                'verbose_name': 'answer option',
                'default_related_name': 'answeroption',
                'constraints': [
                    models.UniqueConstraint(
                        fields=('question', text), name='unique_answer'
                    )
                ],
            },
        ),
    ]
