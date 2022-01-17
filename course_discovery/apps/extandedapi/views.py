from rest_framework.response import Response
from django.conf import settings
from elasticsearch import Elasticsearch
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from course_discovery.apps.course_metadata.models import Program, Course
from course_discovery.apps.api.v1.views.search import CourseSearchViewSet
from rest_framework import status
from collections import OrderedDict
from itertools import chain

# pylint: disable=attribute-defined-outside-init
class GetProgramTopics(APIView):
    """ GET Program Based Topics View."""
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        sub_name = request.GET.get('subject_name')
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
        #es_response['facets']['tags']['terms']   status=status.HTTP_200_OK
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

class GetProgramTags(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self,request):
        prog_uuids = request.GET.get('uuids')
        tags = list()
        if prog_uuids:
            for prog_id in prog_uuids.split(','):
                try:
                    program = Program.objects.get(uuid=prog_id)
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
        return Response(tags,status=status.HTTP_200_OK)

class GetAllPrograms(APIView):
    permission_classes = (AllowAny,)
    def get(self,request):
        programs = Program.objects.all()
        result = dict()
        for program in programs:
            result[str(program.uuid)] = list(chain(*program.courses.all().values_list('key')))
        return Response(result,status=status.HTTP_200_OK)