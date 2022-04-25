from copy import deepcopy

from drf_spectacular.utils import inline_serializer
from rest_framework import fields
from rest_framework.exceptions import ValidationError, APIException, PermissionDenied

from api_fhir_r4.subscriptions import SubscriptionConverter
from api_fhir_r4.models import Subscription
from api_fhir_r4.permissions import FHIRApiInsureePermissions, FHIRApiInvoicePermissions, FHIRApiHealthServicePermissions
from api_fhir_r4.serializers import BaseFHIRSerializer
from api_fhir_r4.services import SubscriptionService


class SubscriptionSerializer(BaseFHIRSerializer):
    fhirConverter = SubscriptionConverter
    _error_while_saving = 'Error while saving a subscription: %(msg)s'

    resource_permissions = {
        'patient': FHIRApiInsureePermissions.permissions_get,
        'invoice': FHIRApiInvoicePermissions.permissions_get,
        'bill': FHIRApiInvoicePermissions.permissions_get,
        'organisation': FHIRApiHealthServicePermissions.permissions_get
    }

    def create(self, validated_data):
        user = self.context['request'].user
        self.check_resource_rights(user, validated_data)
        service = SubscriptionService(user)
        copied_data = deepcopy(validated_data)
        del copied_data['_state'], copied_data['_original_state']
        result = service.create(copied_data)
        return self.get_result_object(result)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        self.check_instance_id(instance, validated_data)
        self.check_object_owner(user, instance)
        self.check_resource_rights(user, validated_data)
        service = SubscriptionService(user)
        copied_data = {key: value for key, value in deepcopy(validated_data).items() if value is not None}
        copied_data['id'] = instance.id
        del copied_data['_state'], copied_data['_original_state']
        result = service.update(copied_data)
        return self.get_result_object(result)

    def get_result_object(self, result):
        if result.get('success', False):
            return Subscription.objects.get(id=result['data']['id'])
        else:
            raise APIException(self._error_while_saving % {'msg': result.get('message', 'Unknown')})

    def check_resource_rights(self, user, data):
        resource_type = data.get('criteria', {}).get('resource_type', '').lower()
        if not resource_type or resource_type not in self.resource_permissions:
            raise ValidationError(self._error_while_saving % {'msg': f'Invalid resource_type ({resource_type})'})

        if not user.has_perms(self.resource_permissions[resource_type]):
            raise PermissionDenied(
                detail=self._error_while_saving % {'msg': f'You have no permissions to subscribe to {resource_type}'})

    def check_object_owner(self, user, instance):
        if str(user.id).lower() != str(instance.user_created.id).lower():
            raise APIException(self._error_while_saving % {'msg': 'You are not the owner of this subscription'})

    def check_instance_id(self, instance, validated_data):
        if validated_data['id'] and str(instance.id) != validated_data['id']:
            raise APIException(self._error_while_saving % {'msg': 'Invalid ID in the payload'})


class SubscriptionSerializerSchema(SubscriptionSerializer):
    resourceType = fields.CharField(read_only=True)
    id = fields.UUIDField(read_only=True)
    status = fields.CharField()
    end = fields.DateTimeField()
    reason = fields.CharField()
    criteria = fields.CharField()
    channel = inline_serializer(
        name='ChannelSerializer',
        fields={
            'type': fields.CharField(),
            'endpoint': fields.CharField(),
            'header': fields.ListField(child=fields.CharField(), min_length=0, max_length=1),
        },
    )