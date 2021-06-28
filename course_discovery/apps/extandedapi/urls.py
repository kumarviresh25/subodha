from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^get-program-topics/$', GetProgramTopics.as_view(), name='get_program_topics',),
]