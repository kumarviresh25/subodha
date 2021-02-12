from django.shortcuts import render
from django.http import HttpResponse
from django.core.management import call_command



def update_scripts(request):
    return render(request, 'update_scripts.html',{})

def discovery_views(request):
    course_meta = call_command('refresh_course_metadata')
    # import pdb; pdb.set_trace()
    return HttpResponse(course_meta)

def update_indexCmd(request):
    updateIndexCmd = call_command('update_index', '--disable-change-limit')
    # import pdb; pdb.set_trace()
    return HttpResponse(updateIndexCmd)
    
