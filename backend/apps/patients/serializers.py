from typing import Optional

from rest_framework import serializers

from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for patient records."""

    id = serializers.UUIDField(source='pk', read_only=True)
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id',
            'organization',
            'identity_type',
            'cedula',
            'passport_number',
            'first_name',
            'last_name',
            'birth_date',
            'sex',
            'nationality',
            'phone_primary',
            'phone_secondary',
            'email',
            'address',
            'province',
            'municipality',
            'blood_type',
            'allergies',
            'chronic_conditions',
            'emergency_contact_name',
            'emergency_contact_phone',
            'emergency_contact_relation',
            'ars_provider',
            'ars_affiliation_number',
            'status',
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

    def get_created_by_name(self, obj: Patient) -> Optional[str]:
        if obj.created_by:
            return f'{obj.created_by.first_name} {obj.created_by.last_name}'
        return None

    def get_updated_by_name(self, obj: Patient) -> Optional[str]:
        if obj.updated_by:
            return f'{obj.updated_by.first_name} {obj.updated_by.last_name}'
        return None

    def validate_cedula(self, value: str) -> str:
        """Validate cedula format for Dominican Republic."""
        if value:
            # Cédula should be 11 digits (no hyphens)
            cleaned = value.replace('-', '').strip()
            if not cleaned.isdigit() or len(cleaned) != 11:
                raise serializers.ValidationError(
                    'La cédula debe tener 11 dígitos (ejemplo: 00112345678)'
                )
        return value

    def validate_passport_number(self, value: str) -> str:
        """Validate passport number format."""
        if value and len(value.strip()) < 6:
            raise serializers.ValidationError(
                'El número de pasaporte debe tener al menos 6 caracteres'
            )
        return value.strip()

    def validate_birth_date(self, value) -> str:
        """Ensure birth date is in the past."""
        from datetime import date
        if value and value >= date.today():
            raise serializers.ValidationError(
                'La fecha de nacimiento debe ser anterior a la fecha actual'
            )
        return value

    def create(self, validated_data: dict) -> Patient:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)

    def update(self, instance: Patient, validated_data: dict) -> Patient:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class PatientLookupSerializer(serializers.ModelSerializer):
    """Minimal patient lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'first_name', 'last_name', 'cedula']
