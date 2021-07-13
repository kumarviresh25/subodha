from django.shortcuts import render
from django.http import HttpResponse
from django.core.management import call_command
from django.core.cache import cache




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

def discovery_views(request):
    call_command('refresh_course_metadata', verbosity=0)
    if cache.get('course_meta_status'):
        return HttpResponse("Running State..........")
    else:
        return HttpResponse("Run SuccessFully")

def update_indexCmd(request):
    call_command('update_index', '--disable-change-limit')
    if cache.get('update_index_status'):
        return HttpResponse("Running State...........")
    else:
        return HttpResponse("Run SuccessFully")
    
