from typing import Optional

from rest_framework import serializers

from .models import Doctor, Specialty


class SpecialtySerializer(serializers.ModelSerializer):
    """Serializer for medical specialties."""

    id = serializers.UUIDField(source='pk', read_only=True)

    class Meta:
        model = Specialty
        fields = [
            'id',
            'code',
            'name',
            'description',
            'is_active',
        ]
        read_only_fields = ['id']


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for medical doctors."""

    id = serializers.UUIDField(source='pk', read_only=True)
    specialty_main_name = serializers.CharField(
        source='specialty_main.name', read_only=True
    )
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = [
            'id',
            'organization',
            'user',
            'cedula',
            'license_number',
            'medical_college_number',
            'first_name',
            'last_name',
            'specialty_main',
            'specialty_main_name',
            'phone',
            'email',
            'office_room',
            'is_active',
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

    def get_created_by_name(self, obj: Doctor) -> Optional[str]:
        if obj.created_by:
            return f'{obj.created_by.first_name} {obj.created_by.last_name}'
        return None

    def get_updated_by_name(self, obj: Doctor) -> Optional[str]:
        if obj.updated_by:
            return f'{obj.updated_by.first_name} {obj.updated_by.last_name}'
        return None

    def validate_cedula(self, value: str) -> str:
        """Validate cedula format for Dominican Republic."""
        if value:
            cleaned = value.replace('-', '').strip()
            if not cleaned.isdigit() or len(cleaned) != 11:
                raise serializers.ValidationError(
                    'La cédula debe tener 11 dígitos (ejemplo: 00112345678)'
                )
        return value

    def validate_license_number(self, value: str) -> str:
        """Validate license number format."""
        if value and len(value.strip()) < 6:
            raise serializers.ValidationError(
                'El número de licencia debe tener al menos 6 caracteres'
            )
        return value.strip()

    def create(self, validated_data: dict) -> Doctor:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['created_by'] = request.user
            validated_data['updated_by'] = request.user
        return super().create(validated_data)

    def update(self, instance: Doctor, validated_data: dict) -> Doctor:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['updated_by'] = request.user
        return super().update(instance, validated_data)


class DoctorLookupSerializer(serializers.ModelSerializer):
    """Minimal doctor lookup for nested display."""

    id = serializers.UUIDField(source='pk', read_only=True)
    specialty_main_name = serializers.CharField(
        source='specialty_main.name', read_only=True
    )

    class Meta:
        model = Doctor
        fields = [
            'id',
            'first_name',
            'last_name',
            'cedula',
            'specialty_main_name',
        ]
