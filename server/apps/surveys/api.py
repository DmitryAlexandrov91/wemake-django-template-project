from rest_framework import routers

from server.apps.surveys.views import SurveyViewSet

router = routers.DefaultRouter()
router.register(
    'surveys',
    SurveyViewSet,
    basename='surveys',
)
