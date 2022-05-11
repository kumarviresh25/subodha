from unittest import result
from rest_framework.response import Response
from django.conf import settings
from elasticsearch import Elasticsearch
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from course_discovery.apps.course_metadata.models import Program, Course, CourseRun, SubjectTranslation, Organization, Subject
from course_discovery.apps.api.v1.views.search import CourseSearchViewSet, AggregateSearchViewSet
from course_discovery.apps.mx_multilingual_discovery.models import MultiLingualDiscovery
from rest_framework import status
from collections import OrderedDict
from itertools import chain
import logging as log
from django.db.models import Q

# pylint: disable=attribute-defined-outside-init
class GetProgramTopics(APIView):
    """ GET Program Based Topics View."""
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        subject_name_param = request.GET.get('subject_name')
        sub = SubjectTranslation.objects.filter(name=subject_name_param)

        try:
            sub_id = sub[0].master.id
            sub_en = Subject.objects.language('en').get(id=sub_id)
            sub_name = sub_en.name
            
        except Exception as e:
            sub_name = subject_name_param
        
        
        body = {
            "query": {"bool": {
                "must": [
                        { "match": {
                            "content_type": "program"
                            }
                        },
                        {"match": {
                            "program_subjects": sub_name
                            }
                        }
                        ]
                    }
                },
            "facets" : {
                "tags" : { "terms" : {"field" : "program_topics_exact"} }
                }
            }
        alias = settings.HAYSTACK_CONNECTIONS['default']['INDEX_NAME']
        
        # index = '{alias}_20160621_000000'.format(alias=alias)

        host = settings.HAYSTACK_CONNECTIONS['default']['URL']
        
        connection = Elasticsearch(host)
        index_value = connection.indices.get_alias(name=alias)
        es_response = connection.search(index=[i for i in index_value.keys()][0], body=body)

        

        try:
            accept_language = request.headers['Accept-Language']
            if not accept_language or accept_language=='en':
                return Response(es_response['facets']['tags'])
        except KeyError:
            return Response(es_response['facets']['tags'])

        

        
        tag = MultiLingualDiscovery.objects.language('en').filter(Q(content_type='Tag')).active_translations(title__in=[i['term'] for i in es_response['facets']['tags']['terms']])

        converted_tag = MultiLingualDiscovery.objects.language(accept_language).filter(Q(content_type='Tag')).active_translations(title__in=[i.title for i in tag])

        # data = tag.__dict__
        # import pdb;pdb.set_trace()
        data = {}
        for j in range(len(converted_tag)):
            data[tag[j].title] = converted_tag[j].title
    
            
        for i in range(len(es_response['facets']['tags']['terms'])):

            if es_response['facets']['tags']['terms'][i]['term'] in data:
                 es_response['facets']['tags']['terms'][i]['converted_term'] = data[es_response['facets']['tags']['terms'][i]['term']]
            else:
                es_response['facets']['tags']['terms'][i]['converted_term'] = ''


        return Response(es_response['facets']['tags'])

class CustomSearch(APIView):
    """
    Custom search based on the courses.

    1. Query parameter (q).

    2. Internal course_search api called to get the data.

    3. After getting result appending program_details to the dict and returning in the following format.

        final_response = {
                "count" : total count of the dict,
                "next" : next url,
                "previous" : previous url,
                "results" : dict type result
            }
    """
    permission_classes = (IsAuthenticated,)
    def get_program_details(self,course_key):
        programs_dict = OrderedDict()
        try:
            course = Course.objects.get(key=course_key)
            programs = Program.objects.filter(courses=course)
            if programs:
                programs_dict['programs'] = [program.title for program in programs]
                programs_dict['program_id'] = [program.uuid for program in programs]
                # for program in programs:
                programs_dict['tags'] = [OrderedDict({
                    "program_name":program.title,
                    "program_id":program.uuid,
                    "tags":[tags.name for tags in program.program_topics.all()] })for program in programs]
              
            return programs_dict
        except Course.DoesNotExist:
            programs_dict = None
            return programs_dict

    def get(self,request):
        programs_details = None
        content = CourseSearchViewSet.as_view({'get': 'list'})(request._request)
        for x in content.data['results']:
            programs_details = self.get_program_details(x['key'])
            x['program_details'] = programs_details
        final_response = OrderedDict()
        final_response["count"] = len(content.data['results'])
        final_response["next"] = content.data['next'] if content.data['next'] else None
        final_response["previous"] = content.data['previous'] if content.data['previous'] else None
        final_response["results"] = content.data['results']
        return Response(final_response,status=status.HTTP_200_OK)      

# Extract all programs and detials based on prorgrma uuid and extract the resume program data based on course block id
class GetProgramTags(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        prog_uuids = request.GET.get('uuids')
        resume_data = request.GET.get('resume_data')
        log.info("Resume data received: {}".format(resume_data))
        log.info("Program UUIDS: {}".format(prog_uuids))
        tags = list()
        if prog_uuids:
            for prog_id in prog_uuids.split(','):
                try:
                    program = Program.objects.get(uuid=prog_id)
                    log.info("Enrolled Program: {}".format(program.title))
                    response = {
                        "program_uuid":prog_id,
                        "program_title":program.title,
                        "tags":[tags.name for tags in program.program_topics.all()]
                    }
                    tags.append(response)
                except Program.DoesNotExist:
                    print("Program not found with uuid: %s",prog_id)
                except Exception as e:
                   print("Error occured due to: %s",e)
            if resume_data:
                resume_str = resume_data.replace(' ','+')
                resume_data = resume_str.split(',')
                log.info("Resume data received {}".format(resume_data))
                temp_course_id = resume_data[0].replace('course-v1:','')
                course_key = '+'.join(temp_course_id.split('+')[0:len(temp_course_id.split('+'))-1])
                course = Course.objects.get(key=course_key)
                programs = Program.objects.filter(courses=course)
                log.info("Course related programs: {}".format(programs))
                resume_course_programs = filter(lambda x:str(x.uuid) in prog_uuids.split(','), programs)
                log.info("Resume course programs: {}".format(resume_course_programs))
                resume_prog_uuid = [str(prog.uuid) for prog in resume_course_programs]
                for prog in tags:
                    if prog['program_uuid'] in resume_prog_uuid:
                        prog['resume_program'] = {
                            "course_id": resume_data[0],
                            "course_name": course.title,
                            "block_id": resume_data[-1],
                        }
        return Response(tags,status=status.HTTP_200_OK)

class GetAllPrograms(APIView):
    permission_classes = (AllowAny,)
    def get(self,request):
        programs = Program.objects.all()
        result = dict()
        for program in programs:
            result[str(program.uuid)] = list(chain(*program.courses.all().values_list('key')))
        return Response(result,status=status.HTTP_200_OK)

class GetCourseReportsData(APIView):
    permission_classes = (AllowAny,)
    def get(self,request):
        courses = CourseRun.objects.all()
        result = list()
        for course in courses:
            courses_data = dict()
            tags = list()
            subjects = list()
            orgs = list()
            courses_data['course_id'] = course.key
            courses_data['course_name'] = course.title_override
            courses_data['start_date'] = course.start
            courses_data['end_date'] = course.end
            programs = Program.objects.filter(courses=course.course)
            courses_data['programs'] = ','.join([prog.title for prog in programs])
            for program in programs:
                program_tag = program.program_topics.all()
                program_subject = program.program_subjects.all()
                program_org = program.authoring_organizations.all()
                tags.extend([tag.name for tag in program_tag])
                subjects.extend([sub.name for sub in program_subject])
                orgs.extend([org.key for org in program_org])
            courses_data['tags'] = ','.join(tags)
            courses_data['subjects'] = ','.join(subjects)
            courses_data['organizations'] = ','.join(orgs)
            result.append(courses_data)
        return Response(result,status=status.HTTP_200_OK)

class GetReportsFilterData(APIView):
    permission_classes = (AllowAny,)
    def get(self,request):
        result = dict()

        programs_obj = Program.objects.all()
        programs = {prog.title:prog.title.upper() for prog in programs_obj}

        orgs_obj = Organization.objects.filter(name__isnull=False)
        orgs = {x.name:x.name.upper() for x in orgs_obj}

        subjects_obj = SubjectTranslation.objects.filter(language_code='en')
        subjects = {sub.name:sub.name.upper() for sub in subjects_obj}

        courses = CourseRun.objects.all()
        courses = {course.title_override:course.title_override.upper() for course in courses}

        result['programs']=programs
        result['orgs']=orgs
        result['subjects']=subjects
        result['courses']=courses

        return Response(result,status=status.HTTP_200_OK)
