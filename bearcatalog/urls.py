from django.conf.urls import url, include

from bearcatalog.views import *
from . import views

app_name = 'bearcatalog'
urlpatterns = [
    url(r'^$', CatalogView.as_view(), name='catalog'),
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # url(r'^api/', views.index, name='api'),
    url(r'^(?P<pk>[0-Z]{2,4})/$', views.subject, name='subject'),
    url(r'^(?P<subject>[0-Z]{2,4})/(?P<number>[0-Z]{4,5})/$', CourseView.as_view(), name='course')
]