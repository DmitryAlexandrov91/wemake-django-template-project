from django.db import models


class QuestionType(models.TextChoices):
    """Choices for type of question."""

    RATING_SCALE = 'ratingScale', 'Rating scale'
    SCORE = 'score', 'Score'
    CONSENT_GIVEN = 'consentGiven', 'Consent given'


class SurveyStatus(models.TextChoices):
    """Choices for survey status."""

    DRAFT = 'draft', 'Draft'
    ACTIVE = 'active', 'Active'
    COMPLETED = 'completed', 'Completed'
    ARCHIVED = 'archived', 'Archived'


class SurveyBotState(models.TextChoices):
    """Choices for survey bot state."""

    WAITING_START = 'waitingStart', 'Waiting start'
    IN_SURVEY = 'inSurvey', 'In survey'
    COMPLETED = 'completed', 'Completed'
    EDITING = 'editing', 'Editing'
