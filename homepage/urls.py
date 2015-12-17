from django.conf.urls import url

from . import views

app_name = 'homepage'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'contact', views.contact_page, name='contact'),
    url(r'about', views.about_page, name='about')
]
