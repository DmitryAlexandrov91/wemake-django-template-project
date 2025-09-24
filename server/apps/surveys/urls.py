from rest_framework.routers import DefaultRouter

from server.apps.surveys.views import (
    QuestionViewSet,
    SurveyViewSet,
)

router = DefaultRouter()
router.register(r'questions', QuestionViewSet, basename='questions')
router.register(r'surveys', SurveyViewSet, basename='surveys')


urlpatterns = router.urls
