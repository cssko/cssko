from django.conf.urls import url
from django.urls import path

from .views import IndexView,WorkExperience, Activities, Contact, Resume

app_name = 'homepage'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('work_experience', WorkExperience.as_view(), name='work_experience'),
    path('activities', Activities.as_view(), name='activities'),
    path('resume', Resume.as_view(), name='resume'),
    path('contact', Contact.as_view(), name='contact'),
]
