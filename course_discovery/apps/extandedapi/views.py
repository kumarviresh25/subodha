from rest_framework.response import Response
from django.conf import settings
from elasticsearch import Elasticsearch
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from haystack import connections as haystack_connections
from course_discovery.apps.course_metadata.models import Program


# pylint: disable=attribute-defined-outside-init
class GetProgramTopics(APIView):
    """ GET Program Based Topics View."""
    permission_classes = [IsAuthenticated]
    
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
                "tags" : { "terms" : {"field" : "program_topics"} }
                }
            }
        alias = settings.HAYSTACK_CONNECTIONS['default']['INDEX_NAME']
        # index = '{alias}_20160621_000000'.format(alias=alias)

        host = settings.HAYSTACK_CONNECTIONS['default']['URL']
        connection = Elasticsearch(host)
        index_value = connection.indices.get_alias(name=alias)
        es_response = connection.search(index=[i for i in index_value.keys()][0], body=body)
        # import pdb; pdb.set_trace()
        #es_response['facets']['tags']['terms']   status=status.HTTP_200_OK
        return Response(es_response['facets']['tags'])