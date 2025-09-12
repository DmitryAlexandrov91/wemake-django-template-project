from rest_framework.routers import DefaultRouter

from server.apps.company.views import DepartmentViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='departments')

urlpatterns = router.urls
