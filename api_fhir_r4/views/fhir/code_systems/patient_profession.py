from api_fhir_r4.serializers import CodeSystemSerializer

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from api_fhir_r4.views import CsrfExemptSessionAuthentication


class CodeSystemOpenIMISPatientProfessionViewSet(viewsets.ViewSet):

    serializer_class = CodeSystemSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = [CsrfExemptSessionAuthentication] + APIView.settings.DEFAULT_AUTHENTICATION_CLASSES

    def list(self, request):
        # we don't use typical instance, we only indicate the model and the field to be mapped into CodeSystem
        serializer = CodeSystemSerializer(
            instance=None,
            **{
                "model_name": 'Profession',
                "code_field": 'id',
                "display_field": 'profession',
                "id": 'openIMISPatientProfession',
                "name": 'openIMISPatientProfession',
                "title": 'openIMIS Patient Profession',
                "description": "Indicates the profession of a Patient. "
                               "Values defined by openIMIS. Can be extended.",
                "url": self.request.build_absolute_uri()
            }
        )
        data = serializer.to_representation(obj=None)
        return Response(data)
