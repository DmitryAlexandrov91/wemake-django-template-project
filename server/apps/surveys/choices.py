from django.db import models


class QuestionType(models.TextChoices):
    """Choices for type of question."""

    RATING_SCALE = 'ratingScale', 'Rating scale'
    SCORE = 'score', 'Score'
    CONSENT_GIVEN = 'consentGiven', 'Consent given'
