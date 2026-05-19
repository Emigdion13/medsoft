from typing import Optional

from rest_framework import serializers

from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointment records."""

    id = serializers.UUIDField(source='pk', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = [
            'id',
            'organization',
            'patient',
            'doctor',
            'start_at',
            'end_at',
            'appointment_type',
            'reason',
            'status',
            'notes',
            'created_by_name',
            'updated_by_name',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'organization',
            'created_by',
            'updated_by',
            'created_at',
            'updated_at',
        ]

    def get_created_by_name(self, obj: Appointment) -> Optional[str]:
        if obj.created_by:
            return f'{obj.created_by.first_name} {obj.created_by.last_name}'
        return None

    def get_updated_by_name(self, obj: Appointment) -> Optional[str]:
        if obj.updated_by:
            return f'{obj.updated_by.first_name} {obj.updated_by.last_name}'
        return None

    def validate(self, attrs: dict) -> dict:
        """Validate appointment times and check for doctor availability."""
        start_at = attrs.get('start_at')
        end_at = attrs.get('end_at')

        if start_at and end_at and end_at <= start_at:
            raise serializers.ValidationError({
                'end_at': 'La hora de finalización debe ser posterior a la de inicio',
            })

        return super().validate(attrs)

    def create(self, validated_data: dict) -> Appointment:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        instance = super().create(validated_data)
        # Force model-level validation (overlap check in clean())
        instance.full_clean()
        return instance

    def update(self, instance: Appointment, validated_data: dict) -> Appointment:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        instance = super().update(instance, validated_data)
        # Force model-level validation (overlap check in clean())
        instance.full_clean()
        return instance


class AppointmentLookupSerializer(serializers.ModelSerializer):
    """Minimal appointment lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'start_at', 'end_at', 'appointment_type', 'reason']
