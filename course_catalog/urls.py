from django.conf.urls import url

from course_catalog.views import catalog_index_view, discipline_table, discipline_courses_view, CourseSectionsView

app_name = 'course_catalog'
urlpatterns = [
    url(r'^$', view=catalog_index_view, name='catalog'),
    url(r'^discipline_table/', view=discipline_table, name='discipline_table'),
    url(r'^discipline/(?P<discipline>[A-Z]{2,4})/$', view=discipline_courses_view, name='discipline'),
    url(r'^course/(?P<course>[A-Z]{2,4}[0-9]{4}[A-Z]?)/$', view=CourseSectionsView.as_view(), name='course')
]
