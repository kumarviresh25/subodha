from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^$', update_scripts, name="update_scripts"),
    url(r'^course-sink$', discovery_views, name="course_sink"),
    url(r'^update-index$', update_indexCmd, name='update_indexCmd')
]