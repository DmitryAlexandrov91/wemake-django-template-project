from django.urls import include, path

from server.apps.surveys.api import router

app_name = 'surveys'


urlpatterns = [path('', include(router.urls))]
