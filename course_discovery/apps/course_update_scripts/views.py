from time import time
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.core.management import call_command
from django.core.cache import cache
from threading import Thread
import time




def update_scripts(request):
    # import pdb; pdb.set_trace()
    course_meta_status = cache.get('course_meta_status')
    course_meta_timestamp = cache.get('course_meta_timestamp')
    update_index_timestamp = cache.get('update_index_timestamp')
    update_index_status = cache.get('update_index_status')


    if update_index_status is not None:
        if update_index_status:
            update_index_command_state = update_index_status
        else:
            update_index_command_state = update_index_status
    else:
        update_index_command_state = False

    if course_meta_status is not None:
        if course_meta_status:
            course_meta_command_state = course_meta_status
        else:
            course_meta_command_state = course_meta_status
    else:
        course_meta_command_state = False
    
    context = {
        "course_meta_command_state":course_meta_command_state,
        "course_meta_timestamp":course_meta_timestamp,
        "update_index_command_state":update_index_command_state,
        "update_index_timestamp":update_index_timestamp
        }
    return render(request, 'update_scripts.html',context)

def callcourse_sync():
    call_command('refresh_course_metadata', verbosity=0)

def callupdate_index():
    call_command('update_index', '--disable-change-limit')

def discovery_views(request):
    Thread(target=callcourse_sync).start()
    time.sleep(2)
    return redirect(update_scripts)

def update_indexCmd(request):
    Thread(target=callupdate_index).start()
    time.sleep(2)
    return redirect(update_scripts)
   
