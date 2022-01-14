from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^get-program-topics/$', GetProgramTopics.as_view(), name='get_program_topics'),
    url(r'^custom-course-search/$', CustomSearch.as_view(), name='custom_course_search'),
    url(r'^getprogramtags/$', GetProgramTags.as_view(), name='getprogramtags'),
]